import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:lush/UserRepository/user_repository.dart';
import 'package:lush/widgets/app_text_field.dart';
import 'package:toastification/toastification.dart';

/// BR-009: Forgot Password - Choose reset method (mobile OTP or email OTP)
class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final UserRepository userRepository = UserRepository();
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  void _sendPhoneOTP() async {
    if (!_formKey.currentState!.validate()) return;

    final phone = _phoneController.text.trim();
    if (!isValidPhone(phone)) {
      _showToast('Invalid phone number', 'Enter a valid 10-digit Indian number', ToastificationType.error);
      return;
    }

    setState(() => _isLoading = true);

    final response = await userRepository.sendOTP(phone);

    setState(() => _isLoading = false);

    if (response.contains('Success') || response.contains('sent')) {
      Navigator.of(context).pushNamed(
        '/reset-password-mobile-otp',
        arguments: {'phone': phone},
      );
    } else {
      _showToast('Failed to send OTP', response, ToastificationType.error);
    }
  }

  void _sendEmailCode() async {
    if (!_formKey.currentState!.validate()) return;

    final email = _emailController.text.trim();
    if (!isValidEmail(email)) {
      _showToast('Invalid email', 'Enter a valid email address', ToastificationType.error);
      return;
    }

    setState(() => _isLoading = true);

    final response = await userRepository.sendEmailVerification(email);

    setState(() => _isLoading = false);

    if (response.contains('Success') || response.contains('sent')) {
      Navigator.of(context).pushNamed(
        '/reset-password-email-code',
        arguments: {'email': email},
      );
    } else {
      _showToast('Failed to send code', response, ToastificationType.error);
    }
  }

  void _showToast(String title, String message, ToastificationType type) {
    toastification.show(
      title: Text(title),
      description: Text(message),
      type: type,
      closeButton: ToastCloseButton(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Forgot Password'),
        backgroundColor: Colors.amber,
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(height: 20),
                Icon(Icons.lock_reset, size: 80, color: Colors.amber),
                SizedBox(height: 20),
                Text(
                  'Reset Your Password',
                  style: FontUtils.heading1(
                    color: Colors.black87,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Choose how you want to verify your identity',
                  style: FontUtils.bodyText(
                    color: Colors.grey[600],
                    fontSize: 14,
                    fontWeight: FontWeight.normal,
                  ),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 30),

                // Method 1: Phone OTP
                _buildMethodCard(
                  icon: Icons.phone_android,
                  title: 'Via Phone OTP',
                  subtitle: 'We\'ll send a 6-digit code to your registered phone',
                  child: AppTextField(
                    label: 'Phone Number',
                    hint: 'Enter your registered phone number',
                    prefixIcon: Icons.phone,
                    keyboardType: TextInputType.phone,
                    controller: _phoneController,
                    maxLength: 10,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    validator: (value) {
                      if (value == null || value.isEmpty) return 'Phone number is required';
                      if (!isValidPhone(value)) return 'Enter a valid 10-digit number';
                      return null;
                    },
                  ),
                  buttonText: 'Send OTP to Phone',
                  onTap: _sendPhoneOTP,
                  isLoading: _isLoading,
                ),

                SizedBox(height: 16),

                Divider(thickness: 1, color: Colors.grey[300]),

                SizedBox(height: 8),
                Text(
                  'OR',
                  style: FontUtils.bodyText(
                    color: Colors.grey[500],
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                SizedBox(height: 8),
                Divider(thickness: 1, color: Colors.grey[300]),
                SizedBox(height: 16),

                // Method 2: Email OTP
                _buildMethodCard(
                  icon: Icons.email_outlined,
                  title: 'Via Email OTP',
                  subtitle: 'We\'ll send a 6-digit code to your registered email',
                  child: AppTextField(
                    label: 'Email Address',
                    hint: 'Enter your registered email address',
                    prefixIcon: Icons.email,
                    keyboardType: TextInputType.emailAddress,
                    controller: _emailController,
                    validator: (value) {
                      if (value == null || value.isEmpty) return 'Email is required';
                      if (!isValidEmail(value)) return 'Enter a valid email address';
                      return null;
                    },
                  ),
                  buttonText: 'Send Code to Email',
                  onTap: _sendEmailCode,
                  isLoading: _isLoading,
                ),

                SizedBox(height: 30),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: Text(
                    'Back to Login',
                    style: FontUtils.bodyText(
                      color: Colors.amber[700],
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                SizedBox(height: 12),
                // BR-009 Fallback: Contact support if user loses access to both phone and email
                TextButton(
                  onPressed: () => _showContactSupportDialog(context),
                  child: Text(
                    "Can't access your phone or email? Contact Support",
                    style: FontUtils.captionText(
                      color: Colors.grey[600]!,
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMethodCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Widget child,
    required String buttonText,
    required VoidCallback onTap,
    required bool isLoading,
  }) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 28, color: Colors.amber[700]),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: FontUtils.heading1(
                        color: Colors.black87,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: FontUtils.captionText(
                        color: Colors.grey[600]!,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          SizedBox(height: 16),
          child,
          SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton(
              onPressed: isLoading ? null : onTap,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.amber,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: isLoading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text(
                      buttonText,
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  void _showContactSupportDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Contact Support'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'If you cannot access your registered phone number or email, please contact our support team to verify your identity and reset your password.',
              style: TextStyle(fontSize: 14, color: Colors.black87, fontFamily: 'Roboto'),
            ),
            SizedBox(height: 16),
            Text(
              '?? Email: support@bookmyjuice.co.in',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.blue[700], fontFamily: 'Roboto'),
            ),
            SizedBox(height: 8),
            Text(
              '?? WhatsApp: +91-XXXXXXXXXX',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.green[700], fontFamily: 'Roboto'),
            ),
            SizedBox(height: 8),
            Text(
              'Please include your registered phone number and email in your message for faster assistance.',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]!, fontFamily: 'Roboto'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }
}




