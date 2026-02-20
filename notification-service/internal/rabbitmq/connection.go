package rabbit

import (
	"fmt"

	amqp "github.com/rabbitmq/amqp091-go"
)


func Connect(url string) (*amqp.Connection, *amqp.Channel, error) {
	connection, err := amqp.Dial(url)
	if err != nil {
		return nil, nil, fmt.Errorf("Error: Connection failed RabbitMQURL: %w", err)
	}

	channel, err := connection.Channel()
	if err != nil {
		connection.Close()
		return nil, nil, fmt.Errorf("Error: Unable to create channel: %w", err)
	}
	return connection, channel, nil
}