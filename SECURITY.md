# Security Policy

## Supported Versions

Currently, we support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public issue
2. Send details to: zohar@babin.co.il
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to expect:

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution Timeline**: Depends on severity
  - Critical: 1-2 weeks
  - High: 2-4 weeks
  - Medium: 1-2 months
  - Low: Next release

## Security Measures

### Authentication & Authorization
- JWT tokens for remote mode authentication
- Secure credential storage using environment variables
- No hardcoded secrets in code

### Input Validation
- Entry ID validation to prevent injection attacks
- Parameter sanitization for all API calls
- Type checking for all inputs

### API Security
- Read-only operations only
- No data modification capabilities
- Rate limiting recommendations for production

### Best Practices
1. Always use HTTPS in production
2. Keep dependencies updated
3. Use strong JWT secrets
4. Enable logging for security events
5. Regular security audits

## Security Checklist for Deployment

- [ ] Use HTTPS for all communications
- [ ] Set strong JWT_SECRET_KEY (32+ characters)
- [ ] Secure .env file permissions (chmod 600)
- [ ] Enable firewall rules
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerting
- [ ] Regular dependency updates
- [ ] Backup configuration

## Disclosure Policy

We follow responsible disclosure:
1. Security issues are fixed before public disclosure
2. Credit given to reporters (if desired)
3. Public disclosure after fix is deployed

Thank you for helping keep Kaltura MCP Server secure!