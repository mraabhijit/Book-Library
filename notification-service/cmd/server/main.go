package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/joho/godotenv"
	"github.com/mraabhijit/notification-service/internal/config"
	"github.com/mraabhijit/notification-service/internal/handler"
	"github.com/mraabhijit/notification-service/internal/notifier"
	rabbit "github.com/mraabhijit/notification-service/internal/rabbitmq"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("No .env file found, using environment varaibles.",)
	}

	cfg, err := config.Load()
	if err != nil {
		log.Fatal("Failed to build config")
	}

	connection, channel, err := rabbit.Connect(cfg.RabbitMQURL)
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer channel.Close()
	defer connection.Close()

	emailNotifier := notifier.NewEmailNotifier(cfg)
	smsNotifier := notifier.NewSMSNotifier(cfg)
	h := handler.NewHandler([]notifier.Notifier{
		emailNotifier,
		smsNotifier,
	})
	go func() {
		if err := rabbit.Consume(channel, "q.book.created", h.HandleBookCreated); err != nil {
			log.Printf("Consumer error (q.book.created): %v", err)
		}
	}()
	go func() {
		if err := rabbit.Consume(channel, "q.book.borrowed", h.HandleBookBorrowed); err != nil {
			log.Printf("Consumer error (q.book.borrowed): %v", err)
		}
	}()
	go func() {
		if err := rabbit.Consume(channel, "q.book.returned", h.HandleBookReturned); err != nil {
			log.Printf("Consumer error (q.book.returned): %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	log.Println("Notification service started. Waiting for messages...")
	<- quit
	log.Println("Shutting down notification service...")
}