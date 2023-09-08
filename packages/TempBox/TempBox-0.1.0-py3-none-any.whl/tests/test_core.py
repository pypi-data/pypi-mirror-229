from TempBox import TempEmail, Attachment, Mailbox


def main():
    temp_email = TempEmail()

    # Generate a random mailbox
    random_mails = temp_email.gen_random_mailbox()
    random_email = random_mails[0]
    print(f"Generated email address: {random_email}")

    # Split the email address into login and domain
    login, domain = random_email.split('@')

    # Create a mailbox instance
    mailbox = Mailbox(login, domain)

    # Loop to keep checking for new messages
    message = mailbox.wait_for_message(sender_filter=None, subject_filter=None, timeout=50, interval=10)
    print(message.text_body)

main()
