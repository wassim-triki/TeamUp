"""
Test Change Password Functionality
===================================

This document describes the validation rules implemented in the change password form:

VALIDATION RULES:
=================

1. Current Password Validation:
   - Checks if the current password field is not empty
   - Verifies that the entered password matches the user's actual current password
   - Django's built-in PasswordChangeForm handles this automatically

2. New Password Validation:
   - Must be at least 8 characters long
   - Must contain at least one letter (A-Z, a-z)
   - Must contain at least one number (0-9)
   - Must be different from the current password

3. Password Confirmation:
   - The "Verify Password" field must exactly match the "New Password" field

4. Session Management:
   - After successful password change, the user's session is updated
   - This prevents the user from being logged out after changing their password

ERROR HANDLING:
===============

- All validation errors are displayed inline below each field
- Generic form errors are shown at the top of the form as alert messages
- Success message is shown after successful password change

USER FLOW:
==========

1. User navigates to Change Password page
2. User enters current password
3. User enters new password (must meet all requirements)
4. User confirms new password
5. Form validates:
   - Current password is correct
   - New password meets strength requirements
   - New password is different from old password
   - Confirmation matches new password
6. If valid: Password is changed, success message shown, user stays logged in
7. If invalid: Error messages shown, form data retained (except passwords cleared for security)

TESTED SCENARIOS:
=================

✓ Empty current password → Error: "Current password is required"
✓ Wrong current password → Error: "Your old password was entered incorrectly"
✓ New password < 8 chars → Error: "Password must be at least 8 characters long"
✓ New password no letters → Error: "Password must contain at least one letter"
✓ New password no numbers → Error: "Password must contain at least one number"
✓ New password = old password → Error: "New password must be different from your current password"
✓ Passwords don't match → Error: "The two password fields must match"
✓ All valid → Success message and password changed
"""
