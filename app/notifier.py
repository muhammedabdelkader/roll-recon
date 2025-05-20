import requests
import smtplib
from email.message import EmailMessage

def notify(results: str, req):
    if req.webhook_url:
        requests.post(req.webhook_url, json={"domain": req.domain, "results": results})

    if req.slack_webhook:
        requests.post(req.slack_webhook, json={"text": f":mag: Recon results for *{req.domain}*:\n```\n{results[:3000]}```"})

    if req.email:
        send_email(req.email, f"Recon Results for {req.domain}", results)

    if req.push_key:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": req.push_token,
            "user": req.push_key,
            "message": f"Recon done for {req.domain}",
            "title": "Recon Notification"
        })

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "muhammed.m.abdelkader@gmail.com"
    msg['To'] = to_email
    msg.set_content(body)

    # Configure your SMTP credentials here (e.g., Gmail, SendGrid, Mailgun)
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "muhammed.m.abdelkader@gmail.com"
    smtp_pass = "code dupu pzsz rpyv"

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)
