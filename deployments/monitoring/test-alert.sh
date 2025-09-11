#!/bin/bash

# Тестируем отправку алертов в Telegram
echo "Testing Telegram alerts..."

# Создаем тестовый алерт
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
        "status": "firing",
        "labels": {
          "alertname": "TestAlert",
          "instance": "test-instance",
          "severity": "critical"
        },
        "annotations": {
          "summary": "Test Alert Summary",
          "description": "This is a test alert to verify Telegram integration",
          "value": "100%"
        },
        "generatorURL": "http://localhost:9090"
      }]'

echo "Test alert sent. Check Telegram for notification."