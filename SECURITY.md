# Security Policy

## Supported Versions

Currently supported versions of hierarchical-memory:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Email**: security@superinstance.ai

Please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Potential impact
- Suggested fix (if known)

### What to Expect

1. **Acknowledgment**: We will respond within 48 hours
2. **Investigation**: We will investigate the issue
3. **Resolution**: We will work on a fix
4. **Disclosure**: We will coordinate disclosure with you

### Guidelines

- Do NOT disclose publicly before coordinated fix
- Do NOT exploit the vulnerability for any reason
- Provide as much detail as possible
- Allow us time to investigate and fix

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version
2. **Review Dependencies**: Regularly update dependencies
3. **Input Validation**: Validate all user inputs
4. **Access Control**: Implement proper access controls
5. **Environment Variables**: Use `.env` files for sensitive data

### For Developers

1. **Dependency Scanning**: Run `pip-audit` regularly
2. **Code Review**: All code should be reviewed
3. **Testing**: Include security tests
4. **Secrets**: Never commit secrets or API keys
5. **Principle of Least Privilege**: Minimize permissions

## Security Features

Hierarchical Memory includes several security features:

- Input validation and sanitization
- Type checking to prevent injection attacks
- Thread-safe operations
- No execution of stored content
- Safe deserialization

## Known Security Considerations

### Vector Embeddings

- Sentence-transformers models are loaded from trusted sources
- User content is not executed, only embedded
- Consider using local models for sensitive data

### Storage Backends

- ChromaDB: Configure authentication for production
- FAISS: Use file permissions for index files
- In-memory: Data is lost on restart, ensure persistence if needed

### Memory Consolidation

- Consolidation strategies operate on stored data only
- No external code execution during consolidation
- Review custom consolidation strategies for security

## Dependencies

We regularly audit and update dependencies. Current dependencies:

- **numpy**: Numerical computing (actively maintained)
- **sentence-transformers** (optional): Vector embeddings
- **chromadb** (optional): Vector database
- **faiss-cpu** (optional): Vector similarity search

For dependency reports, see:
- [DEPENDENCIES.md](DEPENDENCIES.md)
- [GitHub Actions Security](https://github.com/superinstance/hierarchical-memory/security)

## Security Audits

| Date | Version | Auditor | Status |
| ---- | ------- | ------- | ------ |
| TBD  | 1.0.0   | TBD     | Pending|

## Receiving Security Updates

To receive security notifications:

1. **Watch the repository** on GitHub
2. **Subscribe to releases** for version announcements
3. **Monitor SECURITY.md** for policy updates

## Contact

For security-related questions:
- Email: security@superinstance.ai
- GitHub Security Advisory: [Report a vulnerability](https://github.com/superinstance/hierarchical-memory/security/advisories)

## License

This security policy is licensed under the MIT License.
