#!/bin/bash

# Health Check and Monitoring Script
# ==================================
# This script provides monitoring and health check capabilities

set -e

# Configuration
API_URL="${CHATBOT_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="/health"
METRICS_ENDPOINT="/metrics"
LOG_FILE="monitoring.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Health check function
health_check() {
    echo -e "${BLUE}🏥 Running health check...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL$HEALTH_ENDPOINT" || echo "HTTPSTATUS:000")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        log "Health check passed - HTTP $http_code"
        return 0
    else
        echo -e "${RED}❌ Health check failed - HTTP $http_code${NC}"
        log "Health check failed - HTTP $http_code"
        return 1
    fi
}

# Performance test
performance_test() {
    echo -e "${BLUE}⚡ Running performance test...${NC}"
    
    # Test chat endpoint
    test_message='{"message": "Hello, I need help with my order", "session_id": "test-session-123"}'
    
    start_time=$(date +%s.%N)
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${CHATBOT_API_KEY:-test-key}" \
        -d "$test_message" \
        "$API_URL/chat" || echo "HTTPSTATUS:000")
    end_time=$(date +%s.%N)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    response_time=$(echo "($end_time - $start_time) * 1000" | bc)
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Chat endpoint responding - ${response_time}ms${NC}"
        log "Performance test passed - Response time: ${response_time}ms"
    else
        echo -e "${RED}❌ Chat endpoint failed - HTTP $http_code${NC}"
        log "Performance test failed - HTTP $http_code"
    fi
}

# Monitor resources
monitor_resources() {
    echo -e "${BLUE}📊 Monitoring system resources...${NC}"
    
    # CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    echo "CPU Usage: ${cpu_usage}%"
    
    # Memory usage
    memory_usage=$(free | grep Mem | awk '{printf "%.1f", ($3/$2) * 100.0}')
    echo "Memory Usage: ${memory_usage}%"
    
    # Disk usage
    disk_usage=$(df -h / | awk 'NR==2{printf "%s", $5}')
    echo "Disk Usage: $disk_usage"
    
    log "Resources - CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: $disk_usage"
}

# Check application logs
check_logs() {
    echo -e "${BLUE}📋 Checking application logs...${NC}"
    
    if [ -f "chatbot.log" ]; then
        echo "Recent errors:"
        tail -n 20 chatbot.log | grep -i error || echo "No recent errors found"
        
        echo -e "\nRecent activity:"
        tail -n 10 chatbot.log
    else
        echo -e "${YELLOW}⚠️ Log file not found${NC}"
    fi
}

# Connectivity test
connectivity_test() {
    echo -e "${BLUE}🔗 Testing external connectivity...${NC}"
    
    # Test internet connectivity
    if ping -c 1 google.com &> /dev/null; then
        echo -e "${GREEN}✅ Internet connectivity OK${NC}"
    else
        echo -e "${RED}❌ No internet connectivity${NC}"
    fi
    
    # Test Redis connectivity (if configured)
    if [ -n "$CHATBOT_REDIS_URL" ]; then
        redis_host=$(echo $CHATBOT_REDIS_URL | sed 's/redis:\/\///' | cut -d: -f1)
        redis_port=$(echo $CHATBOT_REDIS_URL | sed 's/redis:\/\///' | cut -d: -f2)
        
        if timeout 5 bash -c "</dev/tcp/$redis_host/$redis_port" &> /dev/null; then
            echo -e "${GREEN}✅ Redis connectivity OK${NC}"
        else
            echo -e "${RED}❌ Redis connectivity failed${NC}"
        fi
    fi
}

# Full monitoring suite
run_full_monitoring() {
    echo -e "${BLUE}🚀 Running full monitoring suite...${NC}"
    echo "=========================================="
    
    health_check
    echo ""
    
    performance_test
    echo ""
    
    monitor_resources
    echo ""
    
    connectivity_test
    echo ""
    
    check_logs
    echo ""
    
    echo -e "${GREEN}✅ Monitoring completed${NC}"
}

# Continuous monitoring
continuous_monitoring() {
    echo -e "${BLUE}⏰ Starting continuous monitoring (every 30 seconds)...${NC}"
    echo "Press Ctrl+C to stop"
    
    while true; do
        clear
        echo "=== Continuous Monitoring ==="
        echo "$(date)"
        echo ""
        
        health_check
        monitor_resources
        
        sleep 30
    done
}

# Main menu
show_help() {
    echo "Retail & CPG Chatbot Monitoring Script"
    echo "======================================"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  health        - Run health check only"
    echo "  performance   - Run performance test"
    echo "  resources     - Monitor system resources"
    echo "  logs          - Check application logs"
    echo "  connectivity  - Test external connectivity"
    echo "  full          - Run all monitoring checks"
    echo "  continuous    - Start continuous monitoring"
    echo "  help          - Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  CHATBOT_URL      - Chatbot API URL (default: http://localhost:8000)"
    echo "  CHATBOT_API_KEY  - API key for authentication"
    echo "  CHATBOT_REDIS_URL - Redis URL for connectivity testing"
}

# Handle command line arguments
case "${1:-help}" in
    health)
        health_check
        ;;
    performance)
        performance_test
        ;;
    resources)
        monitor_resources
        ;;
    logs)
        check_logs
        ;;
    connectivity)
        connectivity_test
        ;;
    full)
        run_full_monitoring
        ;;
    continuous)
        continuous_monitoring
        ;;
    help|*)
        show_help
        ;;
esac
