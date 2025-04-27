import requests

# def send_push_notification(expo_token, title, message):
#     payload = {
#         "to": expo_token,
#         "sound": "default",
#         "title": title,
#         "body": message,
#     }
#     response = requests.post("https://exp.host/--/api/v2/push/send", json=payload)
#     print(response.json())import requests

def send_push_notification(expo_token, title, message):
    payload = {
        "to": expo_token,
        "sound": "default",
        "title": title,
        "body": message,
    }

    try:
        response = requests.post("https://exp.host/--/api/v2/push/send", json=payload)
        response.raise_for_status()  # Raise error nếu HTTP status code != 2xx

        result = response.json()
        print("Push notification response:", result)

        # Check Expo response
        if 'errors' in result:
            print("Expo push error:", result['errors'])
        elif result.get("data", {}).get("status") != "ok":
            print("Expo push failed:", result)
        else:
            print("Push notification sent successfully!")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response content: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
