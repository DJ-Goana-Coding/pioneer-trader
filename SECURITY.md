# Security Guidelines

## Environment Variables and Secrets

**IMPORTANT:** Never commit real API credentials to the repository.

### Setup Instructions

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual API credentials:
   - `BINANCE_API_KEY`: Your Binance API key
   - `BINANCE_SECRET`: Your Binance secret key
   - `PORT`: Application port (default: 10000)

3. The `.env` file is listed in `.gitignore` and should never be committed to version control.

### If Credentials Are Exposed

If you accidentally commit API credentials:

1. **Immediately revoke the exposed credentials** in your Binance account
2. Generate new API keys
3. Update your local `.env` file with the new credentials
4. Contact the repository maintainer to clean the git history

## Best Practices

- Always use `.env.example` as a template with placeholder values
- Keep real credentials in `.env` which is git-ignored
- Rotate API keys regularly
- Use API key restrictions when possible (IP whitelist, permission scopes)
