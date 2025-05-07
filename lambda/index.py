# lambda/index.py
import json
import os
import urllib.request  # 追加

FASTAPI_URL = os.environ.get("FASTAPI_URL")

def lambda_handler(event, context):
    try:
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        # FastAPIに渡すJSONを作成
        payload = json.dumps({
            "message": message,
            "conversationHistory": conversation_history
        }).encode("utf-8")

        # FastAPIのエンドポイントにPOSTリクエスト送信
        req = urllib.request.Request(
            url=f"{FASTAPI_URL}/predict",
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode())

        # 返ってきた応答（テキスト）を取り出す
        assistant_response = response_data['response']

        # 会話履歴にアシスタントの返答を追加
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })

        # 成功レスポンスとして返す
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
