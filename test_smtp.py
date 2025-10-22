import smtplib

def test_smtp(host='localhost', port=None, user=None, password=None, use_ssl=False, start_tls=False, timeout=10.0, verbose=True):
    """Test connecting and authenticating to SMTP server."""
    connected = False

    if use_ssl:
        smtp_class = smtplib.SMTP_SSL
        if port is None:
            port = 465
    else:
        smtp_class = smtplib.SMTP
        if port is None:
            port = 587

    if verbose:
        print("SMTP conversation:\n")
        smtp_class.debuglevel = 1

    try:
        smtp = smtp_class(host, port, timeout=timeout)
        connected = True

        if start_tls:
            smtp.starttls()
            smtp.ehlo()

        if user:
            smtp.login(user, password)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except smtplib.SMTPException as exc:
        raise

    return smtp
