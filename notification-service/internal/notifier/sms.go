package notifier

import (
	"fmt"

	"github.com/mraabhijit/notification-service/internal/config"
)

type SMSNotifier struct {
	accountSID string
	authToken  string
	fromNumber string
}

func NewSMSNotifier(cfg *config.Config) *SMSNotifier {
	return &SMSNotifier{
		accountSID: cfg.TwilioAccountSID,
		authToken: cfg.TwilioAuthToken,
		fromNumber: cfg.TwilioFromNumber,
	}
}

func (s *SMSNotifier) Notify(subject string, body string, recipient string) error {
	// TODO Add Twilio service
	message := "Subject: " + subject + "\n" + body + "\n\n"
	fmt.Printf("\nSent SMS\n%s\nFrom: %s\nTo: %s\n", message, s.fromNumber, recipient)
	return nil
}