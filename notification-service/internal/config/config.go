package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	RabbitMQURL 		string
	SMTPHost 			string
	SMTPPort 			int
	SMTPUser 			string
	SMTPPass 			string
	EmailFrom 			string
	TwilioAccountSID 	string
	TwilioAuthToken 	string
	TwilioFromNumber 	string
}

func Load() (*Config, error) {
	rabbitURL := os.Getenv("RABBITMQ_URL")
	if rabbitURL == "" {
		return nil, fmt.Errorf("RABBITMQ_URL is required")
	}

	smtpPortStr := os.Getenv("SMTP_PORT")
	smtpPort := 587 // default
	if smtpPortStr != "" {
		p, err := strconv.Atoi(smtpPortStr)
		if err != nil {
			return nil, fmt.Errorf("SMTP_PORT must be a valid integer: %w", err)
		}
		smtpPort = p
	}

	return &Config{
		RabbitMQURL: rabbitURL,
		SMTPHost: os.Getenv("SMTP_HOST"),
		SMTPPort: smtpPort,
		SMTPUser: os.Getenv("SMTP_USER"),
		SMTPPass: os.Getenv("SMTP_PASS"),
		EmailFrom: os.Getenv("EMAIL_FROM"),
		TwilioAccountSID: os.Getenv("TWILIO_ACCOUNT_SID"),
		TwilioAuthToken:  os.Getenv("TWILIO_AUTH_TOKEN"),
		TwilioFromNumber: os.Getenv("TWILIO_FROM_NUMBER"),
	}, nil
}