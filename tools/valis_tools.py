#!/usr/bin/env python3
"""
VALIS Local Tool Suite - Sprint 7 Implementation
Real tools for memory access and file system operations
"""

import os
import glob
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add memory module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from memory.query_client import memory
from memory.db import db

logger = logging.getLogger("ValisTools")

class ValisToolSuite:
    """
    Local-first tool suite for VALIS agents
    Implements secure file operations and memory queries
    """
    
    def __init__(self):
        # Security configuration
        self.allowed_directories = [
            "C:\\VALIS",
            "C:\\VALIS\\valis2",
            "C:\\VALIS\\logs",
            "C:\\VALIS\\data"
        ]
        self.max_file_size_bytes = 1024 * 1024  # 1MB
        self.max_file_lines = 100
        self.max_search_results = 10
        self.max_directory_entries = 100
        self.max_tokens_output = 1500
        
        logger.info("ValisToolSuite initialized with security constraints")
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        try:
            # Resolve to absolute path
            abs_path = os.path.abspath(path)
            
            # Check against allowed directories
            for allowed_dir in self.allowed_directories:
                allowed_abs = os.path.abspath(allowed_dir)
                if abs_path.startswith(allowed_abs):
                    return True
            
            logger.warning(f"Path access denied: {abs_path}")
            return False
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars = 1 token)"""
        return len(text) // 4
    
    def _truncate_by_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        estimated_tokens = self._estimate_tokens(text)
        if estimated_tokens <= max_tokens:
            return text
        
        # Truncate to roughly max_tokens * 4 characters
        max_chars = max_tokens * 4
        truncated = text[:max_chars]
        
        # Try to truncate at line boundary
        last_newline = truncated.rfind('\n')
        if last_newline > max_chars * 0.8:  # If within 80% of limit
            truncated = truncated[:last_newline]
        
        return truncated + f"\n\n[... truncated at {max_tokens} tokens ...]"
    
    def query_memory(self, user_id: str, topic: str, session_id: str = None) -> Dict[str, Any]:
        """
        Search memory spine for relevant information about a topic
        
        Args:
            user_id: Client UUID for scoped search
            topic: Search term or keyword
            session_id: Optional session ID for emotion-aware filtering
            
        Returns:
            Dict with success, result, and metadata
        """
        try:
            logger.info(f"Memory query: user={user_id[:8]}, topic='{topic}'")
            
            if not topic or not topic.strip():
                return {
                    "success": False,
                    "error": "Topic cannot be empty"
                }
            
            topic_clean = topic.strip().lower()
            search_pattern = f"%{topic_clean}%"
            
            # Check for emotion-aware filtering
            emotion_bias = None
            if session_id:
                try:
                    # Get current emotional state for this session
                    emotion_state = db.query("""
                        SELECT mood, arousal_level, emotion_tags 
                        FROM agent_emotion_state 
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    if emotion_state:
                        current_mood = emotion_state[0]['mood']
                        if current_mood in ['frustrated', 'stressed', 'anxious']:
                            emotion_bias = 'positive'  # Bias towards positive memories when stressed
                        elif current_mood in ['sad', 'tired']:
                            emotion_bias = 'encouraging'  # Bias towards encouraging content
                        elif current_mood in ['excited', 'happy']:
                            emotion_bias = 'energetic'  # Bias towards dynamic content
                        
                        logger.info(f"Memory query with emotion bias: {emotion_bias} (mood: {current_mood})")
                except Exception as e:
                    logger.debug(f"Could not load emotion state for memory filtering: {e}")
                    emotion_bias = None
            
            # Search canon memories (general knowledge) with optional emotion bias
            if emotion_bias:
                # Enhanced query with emotion weighting
                canon_results = db.query("""
                    SELECT cm.content, cm.tags, cm.category, cm.relevance_score,
                           pp.name as persona_name,
                           COALESCE(em.weight, 0) as emotion_weight
                    FROM canon_memories cm
                    LEFT JOIN persona_profiles pp ON cm.persona_id = pp.id
                    LEFT JOIN canon_memory_emotion_map em ON cm.id = em.memory_id 
                        AND em.emotion_tag = %s
                    WHERE LOWER(cm.content) ILIKE %s 
                       OR array_to_string(cm.tags, ' ') ILIKE %s
                    ORDER BY (cm.relevance_score + COALESCE(em.weight * 0.3, 0)) DESC, 
                             cm.last_used DESC
                    LIMIT 5
                """, (emotion_bias, search_pattern, search_pattern))
            else:
                # Standard query without emotion bias
                canon_results = db.query("""
                    SELECT cm.content, cm.tags, cm.category, cm.relevance_score,
                           pp.name as persona_name
                    FROM canon_memories cm
                    LEFT JOIN persona_profiles pp ON cm.persona_id = pp.id
                    WHERE LOWER(cm.content) ILIKE %s 
                       OR array_to_string(cm.tags, ' ') ILIKE %s
                    ORDER BY cm.relevance_score DESC, cm.last_used DESC
                    LIMIT 5
                """, (search_pattern, search_pattern))
            
            # Search working memory (user-specific)
            working_results = db.query("""
                SELECT wm.content, wm.importance, wm.created_at,
                       pp.name as persona_name
                FROM working_memory wm
                LEFT JOIN persona_profiles pp ON wm.persona_id = pp.id
                WHERE wm.client_id = %s 
                  AND LOWER(wm.content) ILIKE %s
                  AND (wm.expires_at IS NULL OR wm.expires_at > NOW())
                ORDER BY wm.importance DESC, wm.created_at DESC
                LIMIT 3
            """, (user_id, search_pattern))
            
            # Format results
            result_parts = []
            
            if canon_results:
                result_parts.append("=== CANON KNOWLEDGE ===")
                for i, cm in enumerate(canon_results, 1):
                    tags_str = ", ".join(cm.get('tags', [])) if cm.get('tags') else "none"
                    result_parts.append(f"{i}. [{cm.get('category', 'general')}] {cm['content']}")
                    result_parts.append(f"   Tags: {tags_str} | Relevance: {cm.get('relevance_score', 0)}")
                    result_parts.append("")
            
            if working_results:
                result_parts.append("=== WORKING MEMORY ===")
                for i, wm in enumerate(working_results, 1):
                    date_str = wm['created_at'].strftime('%Y-%m-%d') if wm.get('created_at') else 'unknown'
                    result_parts.append(f"{i}. {wm['content']}")
                    result_parts.append(f"   From: {wm.get('persona_name', 'unknown')} | Date: {date_str}")
                    result_parts.append("")
            
            if not canon_results and not working_results:
                result_text = f"No memories found matching '{topic}'"
            else:
                result_text = "\n".join(result_parts)
                result_text = self._truncate_by_tokens(result_text, self.max_tokens_output)
            
            return {
                "success": True,
                "result": f"Memory search for '{topic}':\n\n{result_text}",
                "metadata": {
                    "canon_matches": len(canon_results),
                    "working_matches": len(working_results),
                    "topic": topic,
                    "emotion_bias": emotion_bias,
                    "emotion_aware": session_id is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Memory query failed: {e}")
            return {
                "success": False,
                "error": f"Memory search error: {str(e)}"
            }
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read file contents with security and size constraints
        
        Args:
            path: File path to read
            
        Returns:
            Dict with success, result, and metadata
        """
        try:
            logger.info(f"Reading file: {path}")
            
            # Security check
            if not self._is_path_allowed(path):
                return {
                    "success": False,
                    "error": f"Access denied: Path not in allowed directories"
                }
            
            # Check if file exists
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            if not os.path.isfile(path):
                return {
                    "success": False,
                    "error": f"Path is not a file: {path}"
                }
            
            # Check file size
            file_size = os.path.getsize(path)
            if file_size > self.max_file_size_bytes:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max: {self.max_file_size_bytes})"
                }
            
            # Read file content
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(path, 'r', encoding='latin1', errors='replace') as f:
                    lines = f.readlines()
            
            # Limit number of lines
            total_lines = len(lines)
            if total_lines > self.max_file_lines:
                lines = lines[:self.max_file_lines]
                truncated = True
            else:
                truncated = False
            
            content = ''.join(lines)
            
            # Apply token limit
            content = self._truncate_by_tokens(content, self.max_tokens_output)
            
            # Format result
            header = f"File: {path}\nSize: {file_size} bytes | Lines: {total_lines}"
            if truncated:
                header += f" (showing first {self.max_file_lines} lines)"
            
            result_text = f"{header}\n{'='*50}\n{content}"
            
            return {
                "success": True,
                "result": result_text,
                "metadata": {
                    "path": path,
                    "size_bytes": file_size,
                    "total_lines": total_lines,
                    "lines_shown": len(lines),
                    "truncated": truncated
                }
            }
            
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }    
    def search_files(self, keyword: str, search_path: str = None) -> Dict[str, Any]:
        """
        Search for files by name or content within allowed directories
        
        Args:
            keyword: Search term or filename pattern
            search_path: Optional specific path to search (must be allowed)
            
        Returns:
            Dict with success, result, and metadata
        """
        try:
            logger.info(f"File search: keyword='{keyword}', path='{search_path}'")
            
            if not keyword or not keyword.strip():
                return {
                    "success": False,
                    "error": "Search keyword cannot be empty"
                }
            
            keyword = keyword.strip()
            
            # Determine search directories
            if search_path:
                if not self._is_path_allowed(search_path):
                    return {
                        "success": False,
                        "error": "Search path not allowed"
                    }
                search_dirs = [search_path]
            else:
                search_dirs = [d for d in self.allowed_directories if os.path.exists(d)]
            
            results = []
            
            # Check if keyword looks like a filename pattern
            is_pattern = any(char in keyword for char in ['*', '?', '.'])
            
            if is_pattern:
                # Filename pattern search
                for search_dir in search_dirs:
                    try:
                        pattern_path = os.path.join(search_dir, '**', keyword)
                        matches = glob.glob(pattern_path, recursive=True)
                        
                        for match in matches[:self.max_search_results]:
                            if os.path.isfile(match) and self._is_path_allowed(match):
                                size = os.path.getsize(match)
                                results.append({
                                    "type": "filename_match",
                                    "path": match,
                                    "size": size,
                                    "directory": os.path.dirname(match)
                                })
                    except Exception as e:
                        logger.warning(f"Pattern search error in {search_dir}: {e}")
            else:
                # Content search in text files
                for search_dir in search_dirs:
                    try:
                        for root, dirs, files in os.walk(search_dir):
                            # Skip hidden directories
                            dirs[:] = [d for d in dirs if not d.startswith('.')]
                            
                            for file in files:
                                if len(results) >= self.max_search_results:
                                    break
                                
                                file_path = os.path.join(root, file)
                                
                                # Skip binary files and large files
                                if not self._is_text_file(file_path):
                                    continue
                                
                                if not self._is_path_allowed(file_path):
                                    continue
                                
                                # Search file content
                                content_match = self._search_file_content(file_path, keyword)
                                if content_match:
                                    results.append({
                                        "type": "content_match",
                                        "path": file_path,
                                        "line": content_match["line_number"],
                                        "context": content_match["context"],
                                        "size": os.path.getsize(file_path)
                                    })
                    except Exception as e:
                        logger.warning(f"Content search error in {search_dir}: {e}")
            
            # Format results
            if not results:
                result_text = f"No files found matching '{keyword}'"
            else:
                result_parts = [f"Search results for '{keyword}' ({len(results)} matches):"]
                result_parts.append("")
                
                for i, result in enumerate(results, 1):
                    if result["type"] == "filename_match":
                        result_parts.append(f"{i}. [FILE] {result['path']}")
                        result_parts.append(f"   Size: {result['size']} bytes")
                    else:  # content_match
                        result_parts.append(f"{i}. [CONTENT] {result['path']} (line {result['line']})")
                        result_parts.append(f"   Context: {result['context']}")
                    result_parts.append("")
                
                result_text = "\n".join(result_parts)
                result_text = self._truncate_by_tokens(result_text, self.max_tokens_output)
            
            return {
                "success": True,
                "result": result_text,
                "metadata": {
                    "keyword": keyword,
                    "search_type": "pattern" if is_pattern else "content",
                    "matches_found": len(results),
                    "search_dirs": search_dirs
                }
            }
            
        except Exception as e:
            logger.error(f"File search failed: {e}")
            return {
                "success": False,
                "error": f"Search error: {str(e)}"
            }
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        try:
            # Check file extension
            text_extensions = {'.txt', '.py', '.js', '.json', '.xml', '.html', '.css', 
                             '.md', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.log',
                             '.sql', '.csv', '.tsv', '.sh', '.bat', '.ps1'}
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext in text_extensions:
                return True
            
            # For files without extension, try to read a small sample
            if not ext:
                try:
                    with open(file_path, 'rb') as f:
                        sample = f.read(512)
                    # Check if sample contains mostly printable characters
                    printable_ratio = sum(1 for b in sample if 32 <= b <= 126 or b in [9, 10, 13]) / len(sample)
                    return printable_ratio > 0.7
                except:
                    return False
            
            return False
            
        except Exception:
            return False
    
    def _search_file_content(self, file_path: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Search for keyword in file content"""
        try:
            # Skip large files
            if os.path.getsize(file_path) > self.max_file_size_bytes:
                return None
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if keyword.lower() in line.lower():
                        # Return first match with context
                        context = line.strip()
                        if len(context) > 100:
                            # Find keyword position for better context
                            keyword_pos = context.lower().find(keyword.lower())
                            start = max(0, keyword_pos - 30)
                            end = min(len(context), keyword_pos + len(keyword) + 30)
                            context = "..." + context[start:end] + "..."
                        
                        return {
                            "line_number": line_num,
                            "context": context
                        }
            
            return None
            
        except Exception:
            return None
    
    def list_directory(self, path: str) -> Dict[str, Any]:
        """
        List directory contents with security constraints
        
        Args:
            path: Directory path to list
            
        Returns:
            Dict with success, result, and metadata
        """
        try:
            logger.info(f"Listing directory: {path}")
            
            # Security check
            if not self._is_path_allowed(path):
                return {
                    "success": False,
                    "error": "Access denied: Path not in allowed directories"
                }
            
            # Check if directory exists
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"Directory not found: {path}"
                }
            
            if not os.path.isdir(path):
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            # Get directory entries
            try:
                entries = os.listdir(path)
            except PermissionError:
                return {
                    "success": False,
                    "error": f"Permission denied: {path}"
                }
            
            # Process entries
            dirs = []
            files = []
            
            for entry in entries:
                entry_path = os.path.join(path, entry)
                try:
                    if os.path.isdir(entry_path):
                        dirs.append(entry)
                    elif os.path.isfile(entry_path):
                        size = os.path.getsize(entry_path)
                        files.append((entry, size))
                except (OSError, PermissionError):
                    # Skip entries we can't access
                    continue
            
            # Sort and limit results
            dirs.sort()
            files.sort(key=lambda x: x[0])  # Sort by name
            
            total_entries = len(dirs) + len(files)
            if total_entries > self.max_directory_entries:
                # Prioritize directories, then files
                dirs = dirs[:self.max_directory_entries // 2]
                remaining = self.max_directory_entries - len(dirs)
                files = files[:remaining]
                truncated = True
            else:
                truncated = False
            
            # Format result
            result_parts = [f"Directory: {path}"]
            result_parts.append(f"Entries: {total_entries} ({'truncated' if truncated else 'complete'})")
            result_parts.append("")
            
            if dirs:
                result_parts.append("DIRECTORIES:")
                for d in dirs:
                    result_parts.append(f"  [DIR]  {d}")
                result_parts.append("")
            
            if files:
                result_parts.append("FILES:")
                for name, size in files:
                    size_str = self._format_file_size(size)
                    result_parts.append(f"  [FILE] {name} ({size_str})")
            
            if not dirs and not files:
                result_parts.append("(empty directory)")
            
            result_text = "\n".join(result_parts)
            
            return {
                "success": True,
                "result": result_text,
                "metadata": {
                    "path": path,
                    "total_entries": total_entries,
                    "directories": len(dirs),
                    "files": len(files),
                    "truncated": truncated
                }
            }
            
        except Exception as e:
            logger.error(f"Directory listing failed: {e}")
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}"
            }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# Global instance for use by MCPExecutionProvider
valis_tools = ValisToolSuite()
