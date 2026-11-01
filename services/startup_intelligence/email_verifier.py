import dns.resolver
import smtplib
import socket
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_verifier")

def get_mx_records(domain: str) -> list[str]:
    """
    Retrieves MX records for a domain, sorted by preference.
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        # Sort by preference
        sorted_answers = sorted(answers, key=lambda r: r.preference)
        return [str(r.exchange).rstrip('.') for r in sorted_answers]
    except Exception as e:
        logger.warning(f"Failed to resolve MX records for {domain}: {str(e)}")
        # Fallback to domain itself if no MX records resolved
        return []

def verify_single_email_smtp(email: str, mx_servers: list[str]) -> bool:
    """
    Attempts to verify if an email address exists using SMTP handshake on the given MX servers.
    """
    if not mx_servers:
        return False
        
    # We try the primary MX server first
    mx_server = mx_servers[0]
    try:
        # Establish connection with a 3.0s timeout
        server = smtplib.SMTP(timeout=3.0)
        server.connect(mx_server)
        
        # Say hello
        hostname = socket.gethostname()
        server.helo(hostname)
        
        # Set sender (use a generic verification address)
        server.mail("prospector-verify@gmail.com")
        
        # Ask if recipient exists
        code, message = server.rcpt(email)
        server.quit()
        
        # 250 means OK, mailbox exists
        if code == 250:
            return True
        return False
    except Exception as e:
        logger.debug(f"SMTP check failed for {email} on {mx_server}: {str(e)}")
        return False

async def verify_email_async(email: str, mx_servers: list[str]) -> bool:
    """
    Runs the synchronous SMTP verification in a separate thread.
    """
    return await asyncio.to_thread(verify_single_email_smtp, email, mx_servers)

async def guess_and_verify_emails(domain: str, startup_name: str = "") -> list[str]:
    """
    Generates common professional email guesses for a domain and verifies them using SMTP handshakes.
    Returns a list of verified email addresses.
    """
    if not domain:
        return []
        
    # Clean domain
    domain = domain.lower().replace("https://", "").replace("http://", "").split("/")[0]
    if domain.startswith("www."):
        domain = domain[4:]
        
    # Standard role-based aliases to scan
    target_aliases = ['contact', 'hello', 'info', 'support', 'team', 'sales']
    
    # If startup_name looks like a person's name, add personal name guesses
    cleaned_name = startup_name.strip().lower() if startup_name else ""
    if cleaned_name and len(cleaned_name.split()) <= 2 and not any(w in cleaned_name for w in ["inc", "llc", "co", "ltd", "startup", "technology", "tech"]):
        parts = cleaned_name.split()
        first_name = parts[0]
        target_aliases.append(first_name)
        if len(parts) > 1:
            last_name = parts[1]
            target_aliases.append(f"{first_name}.{last_name}")
            target_aliases.append(f"{first_name[0]}{last_name}")
            
    # Deduplicate aliases
    seen = set()
    aliases = [x for x in target_aliases if not (x in seen or seen.add(x))]
    
    guesses = [f"{alias}@{domain}" for alias in aliases]
    
    logger.info(f"Resolving MX records for {domain}...")
    mx_servers = await asyncio.to_thread(get_mx_records, domain)
    if not mx_servers:
        logger.warning(f"No mail servers found for {domain}. Skipping SMTP verification.")
        return []
        
    logger.info(f"Verifying {len(guesses)} guessed emails for {domain} concurrently...")
    
    tasks = [verify_email_async(email, mx_servers) for email in guesses]
    results = await asyncio.gather(*tasks)
    
    verified_emails = [guesses[i] for i, is_valid in enumerate(results) if is_valid]
    
    logger.info(f"Verification complete for {domain}. Found verified emails: {verified_emails}")
    return verified_emails
