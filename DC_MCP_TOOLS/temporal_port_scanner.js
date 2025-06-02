#!/usr/bin/env node
/**
 * DOC BROWN'S TEMPORAL PORT SCANNER
 * Advanced port scanning for VALIS MCP temporal diagnostics
 * 
 * Usage: node temporal_port_scanner.js [host] [start_port] [end_port]
 * Default: scans localhost ports 1-10000
 */

const net = require('net');
const { promisify } = require('util');

class TemporalPortScanner {
    constructor() {
        this.results = {
            open_ports: [],
            closed_ports: [],
            scan_stats: {}
        };
    }

    async scanPort(host, port, timeout = 1000) {
        return new Promise((resolve) => {
            const socket = new net.Socket();
            let result = false;
            
            socket.setTimeout(timeout);
            
            socket.on('connect', () => {
                result = true;
                socket.destroy();
            });
            
            socket.on('timeout', () => {
                socket.destroy();
            });
            
            socket.on('error', () => {
                // Port is closed or filtered
            });
            
            socket.on('close', () => {
                resolve(result);
            });
            
            socket.connect(port, host);
        });
    }

    async scanRange(host, startPort, endPort, concurrency = 100) {
        console.log(`🔬 DOC BROWN'S TEMPORAL PORT SCANNER`);
        console.log(`⚡ Scanning ${host}:${startPort}-${endPort}`);
        console.log(`🚀 Concurrency: ${concurrency}`);
        console.log(`📡 Initiating temporal scan...`);
        
        const scanStart = Date.now();
        const ports = [];
        
        for (let port = startPort; port <= endPort; port++) {
            ports.push(port);
        }
        
        // Process ports in chunks for controlled concurrency
        const chunks = [];
        for (let i = 0; i < ports.length; i += concurrency) {
            chunks.push(ports.slice(i, i + concurrency));
        }
        
        let scannedCount = 0;
        const totalPorts = ports.length;
        
        for (const chunk of chunks) {
            const promises = chunk.map(async (port) => {
                const isOpen = await this.scanPort(host, port);
                scannedCount++;
                
                if (scannedCount % 500 === 0 || isOpen) {
                    process.stdout.write(`\r🔍 Scanned ${scannedCount}/${totalPorts} ports...`);
                }
                
                if (isOpen) {
                    this.results.open_ports.push(port);
                    console.log(`\n✅ OPEN: ${host}:${port}`);
                }
                
                return { port, isOpen };
            });
            
            await Promise.all(promises);
        }
        
        const scanEnd = Date.now();
        const scanTime = (scanEnd - scanStart) / 1000;
        
        this.results.scan_stats = {
            host,
            start_port: startPort,
            end_port: endPort,
            total_ports: totalPorts,
            open_ports_count: this.results.open_ports.length,
            scan_time_seconds: scanTime,
            ports_per_second: Math.round(totalPorts / scanTime)
        };
        
        console.log(`\n\n⚡ TEMPORAL SCAN COMPLETE! ⚡`);
        this.printResults();
    }

    printResults() {
        const { scan_stats, open_ports } = this.results;
        
        console.log(`\n🎯 SCAN RESULTS:`);
        console.log(`📊 Host: ${scan_stats.host}`);
        console.log(`📊 Port Range: ${scan_stats.start_port}-${scan_stats.end_port}`);
        console.log(`📊 Total Ports: ${scan_stats.total_ports}`);
        console.log(`📊 Open Ports: ${scan_stats.open_ports_count}`);
        console.log(`📊 Scan Time: ${scan_stats.scan_time_seconds}s`);
        console.log(`📊 Speed: ${scan_stats.ports_per_second} ports/sec`);
        
        if (open_ports.length > 0) {
            console.log(`\n🔓 OPEN PORTS DETECTED:`);
            open_ports.sort((a, b) => a - b);
            
            open_ports.forEach(port => {
                const service = this.getServiceName(port);
                console.log(`   🌐 ${port}/tcp - ${service}`);
            });
            
            console.log(`\n🔍 DETAILED ANALYSIS:`);
            this.analyzeOpenPorts();
        } else {
            console.log(`\n🛡️  NO OPEN PORTS DETECTED`);
        }
    }

    getServiceName(port) {
        const commonPorts = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            993: 'IMAPS',
            995: 'POP3S',
            3000: 'React Development Server (Vite)',
            3001: 'Alternative Web Dev Server',
            3002: 'Alternative Web Dev Server',
            3313: 'Custom VALIS Backend',
            5000: 'Flask/Development Server',
            8000: 'VALIS Backend API',
            8080: 'HTTP Proxy/Alternative',
            8443: 'HTTPS Alternative'
        };
        
        return commonPorts[port] || 'Unknown Service';
    }

    analyzeOpenPorts() {
        const { open_ports } = this.results;
        
        // VALIS-specific analysis
        const valisBackend = open_ports.includes(8000);
        const valisFrontend = open_ports.includes(3000);
        const valisAlt = open_ports.includes(3313);
        
        if (valisBackend) {
            console.log(`   ✅ VALIS Backend detected on port 8000`);
        }
        
        if (valisFrontend) {
            console.log(`   ✅ VALIS Frontend detected on port 3000`);
        }
        
        if (valisAlt) {
            console.log(`   ✅ VALIS Alternative Backend on port 3313`);
        }
        
        // Check for potential MCP servers
        const mcpPorts = [3001, 3002, 8001, 8002];
        const detectedMCP = open_ports.filter(port => mcpPorts.includes(port));
        
        if (detectedMCP.length > 0) {
            console.log(`   🔌 Potential MCP servers: ${detectedMCP.join(', ')}`);
        }
        
        // Security analysis
        const webPorts = open_ports.filter(port => [80, 443, 8080, 8443].includes(port));
        if (webPorts.length > 0) {
            console.log(`   🌐 Web services detected: ${webPorts.join(', ')}`);
        }
    }

    async quickScan(host = 'localhost') {
        console.log(`🚀 QUICK TEMPORAL SCAN of common ports...`);
        
        const commonPorts = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
                           3000, 3001, 3002, 3313, 5000, 8000, 8080, 8443];
        
        const results = await Promise.all(
            commonPorts.map(async (port) => {
                const isOpen = await this.scanPort(host, port, 500);
                return { port, isOpen };
            })
        );
        
        const openPorts = results.filter(r => r.isOpen).map(r => r.port);
        
        console.log(`\n📊 Quick scan results for ${host}:`);
        if (openPorts.length > 0) {
            openPorts.forEach(port => {
                const service = this.getServiceName(port);
                console.log(`   🔓 ${port}/tcp - ${service}`);
            });
        } else {
            console.log(`   🛡️  No common ports open`);
        }
        
        return openPorts;
    }
}

// Main execution
async function main() {
    const scanner = new TemporalPortScanner();
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log(`🔬 DOC BROWN'S TEMPORAL PORT SCANNER`);
        console.log(`⚡ Usage: node temporal_port_scanner.js [command] [options]`);
        console.log(`\n📡 Commands:`);
        console.log(`   quick [host]                    - Quick scan of common ports`);
        console.log(`   full [host] [start] [end]       - Full range scan`);
        console.log(`   valis [host]                    - VALIS-specific scan`);
        console.log(`\n🚀 Examples:`);
        console.log(`   node temporal_port_scanner.js quick`);
        console.log(`   node temporal_port_scanner.js quick localhost`);
        console.log(`   node temporal_port_scanner.js full localhost 1 10000`);
        console.log(`   node temporal_port_scanner.js valis`);
        return;
    }
    
    const command = args[0];
    
    switch (command) {
        case 'quick':
            const host = args[1] || 'localhost';
            await scanner.quickScan(host);
            break;
            
        case 'full':
            const fullHost = args[1] || 'localhost';
            const startPort = parseInt(args[2]) || 1;
            const endPort = parseInt(args[3]) || 10000;
            await scanner.scanRange(fullHost, startPort, endPort);
            break;
            
        case 'valis':
            const valisHost = args[1] || 'localhost';
            console.log(`🔬 VALIS-SPECIFIC TEMPORAL SCAN`);
            const valisPorts = [3000, 3001, 3002, 3313, 8000, 8001, 8080];
            
            for (const port of valisPorts) {
                const isOpen = await scanner.scanPort(valisHost, port);
                const service = scanner.getServiceName(port);
                const status = isOpen ? '✅ OPEN' : '❌ CLOSED';
                console.log(`   ${status}: ${port}/tcp - ${service}`);
            }
            break;
            
        default:
            console.log(`❌ Unknown command: ${command}`);
            break;
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = TemporalPortScanner;