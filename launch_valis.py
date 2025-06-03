#!/usr/bin/env python3
"""Complete VALIS Frontend Launch"""

import webbrowser
import time

def main():
    print("VALIS Frontend Ready")
    print("Backend: http://127.0.0.1:3001") 
    print("Frontend: http://127.0.0.1:3001")
    print("\nFeatures:")
    print("- 3-panel layout: Personas | Chat | Memory Diagnostics")
    print("- Real-time memory visualization (5 layers)")
    print("- Dev tools: Force #canon, test prompts")
    print("- Memory tag detection")
    
    try:
        webbrowser.open("http://127.0.0.1:3001")
    except:
        print("Open http://127.0.0.1:3001 manually")

if __name__ == "__main__":
    main()
