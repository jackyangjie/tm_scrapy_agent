#!/bin/bash
curl -X 'POST' \
  'http://127.0.0.1:8080/ag-ui' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "context": [],
  "messages": [
    {
      "content": "你是谁",
      "id": "msg_2",
      "role": "user"
    }
  ],
  "runId": "run_456",
  "threadId": "thread_123",
  "tools": []
}'
