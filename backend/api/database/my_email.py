import aiosmtplib
import asyncio
from email.message import EmailMessage


def generate_reset_email_html(reset_code):
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f4;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    color: #fff;
                    background-color: #007bff;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 0.8em;
                    text-align: center;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Use the code below to reset it:</p>
                <p><strong>{reset_code}</strong></p>
                <p>Or click the button below to reset your password:</p>
                <a href="https://yourwebsite.com/reset?code={reset_code}" class="button">Reset Password</a>
                <div class="footer">
                    <p>If you did not request a password reset, please ignore this email or contact support if you have questions.</p>
                </div>
            </div>
        </body>
    </html>
    """


def generate_welcome_email_html(username):
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f4;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    color: #444;
                    text-align: center;
                }}
                .content {{
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 0.8em;
                    text-align: center;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Welcome to Our Service, {username}!</h2>
                </div>
                <div class="content">
                    <p>Thank you for registering with us. We're excited to have you on board and look forward to providing you with an exceptional experience.</p>
                    <p>To get started, you might want to check out the following resources:</p>
                    <ul>
                        <li><a href="https://yourwebsite.com/getting-started">Getting Started Guide</a></li>
                        <li><a href="https://yourwebsite.com/support">Support and FAQs</a></li>
                    </ul>
                </div>
                <div class="footer">
                    <p>If you have any questions, feel free to reply to this email or contact our support team.</p>
                </div>
            </div>
        </body>
    </html>
    """


import ssl


async def send_email(email_address: str, subject: str, code: str, email_type: str):
    message = EmailMessage()
    message["From"] = "277516369@qq.com"  # 你的QQ邮箱地址
    message["To"] = email_address
    message["Subject"] = subject

    if email_type == "1":
        html_content = generate_reset_email_html(code)
    else:
        html_content = generate_welcome_email_html(code)

    # 正确的添加HTML内容到邮件
    message.add_alternative(html_content, subtype='html')
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    await aiosmtplib.send(
        message,
        hostname="smtp.qq.com",  # QQ邮箱SMTP服务器
        port=465,  # SSL端口号
        username="277516369@qq.com",  # 你的QQ邮箱地址
        password="goinphqgcuqkbjch",
        # password="bzjurkkkpohhbhcg", goinphqgcuqkbjch # 你的QQ邮箱SMTP服务授权码
        use_tls=True,  # 使用TLS加密
        validate_certs=False,
        tls_context=context
        # 禁用SSL证书验证
    )


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email_smtplib(email_address, subject, html_content):
    message = MIMEMultipart()
    message['From'] = "277516369@qq.com"
    message['To'] = email_address
    message['Subject'] = subject
    message.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login("277516369@qq.com", "你的授权码")
        server.send_message(message)


async def main():
    # 使用await关键字调用异步函数
    await send_email("277516369@qq.com", "Hello", "6666", "0")


if __name__ == '__main__':
    asyncio.run(main())
    # send_email_smtplib("277516369@qq.com", "Hello", "6666")
