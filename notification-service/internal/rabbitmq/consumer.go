package rabbit

import (
	"fmt"

	amqp "github.com/rabbitmq/amqp091-go"
)

type HandlerFunc func(data []byte) error

func Consume(channel *amqp.Channel, queueName string, handler HandlerFunc) error {
	err := channel.Qos(10, 0, false) // prefetchCount, prefetchSize int, global bool 
	if err != nil {
		return fmt.Errorf("Error: Setting Qos failed: %w", err)
	}

	messages, err := channel.Consume(queueName, "", false, false, false, false, nil)
	if err != nil {
		return fmt.Errorf("Error: Consume: %w", err)
	}

	for message := range messages {
		if err := handler(message.Body); err != nil {
			_ = message.Nack(false, false)
			fmt.Printf("Error: %v\n", err)
		} else {
			_ = message.Ack(false)
		}
		
	}
	return nil
}
