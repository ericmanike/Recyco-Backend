
def reset_password_body(reset_link: str, name:str):
 html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);">
        
        <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); padding: 40px 30px; text-align: center;">
            <div style="display: inline-block; background-color: #ffffff; padding: 12px 24px; border-radius: 8px; margin-bottom: 20px;">
                <h1 style="margin: 0; color: #16a34a; font-size: 28px; font-weight: 700;">🪴 Recyco 💸</h1>
            </div>
            <h2 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">Password Reset Request</h2>
        </div>
        
        <div style="padding: 40px 30px;">
            <p style="margin: 0 0 24px; color: #374151; font-size: 16px; line-height: 1.6;">Hello {name},</p>
            
            <p style="margin: 0 0 24px; color: #374151; font-size: 16px; line-height: 1.6;">
                You requested to reset your password. Click the button below to create a new password:
            </p>

            <div style="text-align: center; margin: 32px 0;">
                <a href="{reset_link}"
                    style="display: inline-block; padding: 16px 40px; background-color: #22c55e; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);">
                    Reset My Password
                </a>
            </div>
            
            <p style="margin: 24px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                This link will expire in 10 minutes for security reasons.
            </p>
            
            <div style="margin: 32px 0; height: 1px; background-color: #e5e7eb;"></div>
            
            <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                <strong style="color: #374151; font-size:16px">Didn't request this?</strong><br>
                If you didn't request a password reset, you can safely ignore this email. 
            </p>
        </div>
        
        <div style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
            <p style="margin: 0 0 12px; color: #9ca3af; font-size: 13px; line-height: 1.5;">
                This email was sent by Recyco<br>
                Helping you recycle smarter, together 🌱
            </p>
            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                © 2024 Recyco. All rights reserved.
            </p>
        </div>
        
        </div>
        """


 return  html_body



