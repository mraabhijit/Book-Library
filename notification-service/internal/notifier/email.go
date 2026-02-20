package notifier

import (
	"fmt"
	"strconv"

	"github.com/mraabhijit/notification-service/internal/config"
)

type EmailNotifier struct {
	host string
	port int
	user string
	pass string
	from string
}

func NewEmailNotifier(cfg *config.Config) *EmailNotifier {
	return &EmailNotifier{
		host: cfg.SMTPHost,
		port: cfg.SMTPPort,
		user: cfg.SMTPUser,
		pass: cfg.SMTPPass,
		from: cfg.EmailFrom,
	}
}

func (e *EmailNotifier) Notify(subject string, body string, recipient string) error {
	msg := []byte(
		"Subject: " + subject + "\n\n" + body + "\n\n",
	)

	// auth := smtp.PlainAuth("", e.user, e.pass, e.host)
	address := e.host + ":" + strconv.Itoa(e.port)
	fmt.Printf("\nSent Email\n%s\nFrom: %s\nTo: %s\n", msg, address, recipient)
	// err := smtp.SendMail(address, auth, e.from, []string{recipient}, msg)
	// if err != nil {
	// 	return fmt.Errorf("SMTP Error: %w", err)
	// }
	return nil
}