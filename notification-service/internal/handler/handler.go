package handler

import (
	"encoding/json"
	"fmt"

	"github.com/mraabhijit/notification-service/internal/models"
	"github.com/mraabhijit/notification-service/internal/notifier"
)

type Handler struct {
	notifiers []notifier.Notifier
}

func NewHandler(notifiers []notifier.Notifier) *Handler {
	return &Handler{
		notifiers: notifiers,
	}
}

func (h *Handler) HandleBookCreated(data []byte) error {
	var bookCreatedEvent models.BookCreatedEvent 
	err := json.Unmarshal(data, &bookCreatedEvent)
	if err != nil {
		return fmt.Errorf("Unmarshall error: %w", err)
	}

	for _, n := range h.notifiers {
		subject := "New Book Added!"
		body := "Title: " + bookCreatedEvent.Title + "\n" + "Author: " + bookCreatedEvent.Author
		recipient := "user@example.com"
		if err := n.Notify(subject, body, recipient); err != nil {
			fmt.Printf("Error sending notification to %v", recipient)
		}
	}
	return nil
}

func (h *Handler) HandleBookBorrowed(data []byte) error {
	var bookBorrowed models.BookBorrowedEvent 
	err := json.Unmarshal(data, &bookBorrowed)
	if err != nil {
		return fmt.Errorf("Unmarshall error: %w", err)
	}

	for _, n := range h.notifiers {
		subject := "Book Borrowed!"
		body := (
			"Book: " + bookBorrowed.BookTitle + "\n" + 
			"Member: " + bookBorrowed.MemberName + "\n" + 
			"Due Date: " + bookBorrowed.DueDate)
		if err := n.Notify(subject, body, bookBorrowed.MemberPhone); err != nil {
			fmt.Printf("Error sending notification to %v", bookBorrowed.MemberPhone)
		}
	}
	return nil
}


func (h *Handler) HandleBookReturned(data []byte) error {
	var bookReturned models.BookReturnedEvent
	err := json.Unmarshal(data, &bookReturned)
	if err != nil {
		return fmt.Errorf("Unmarshall error: %w", err)
	}

	for _, n := range h.notifiers {
		subject := "Book Returned!"
		body := (
			"Book: " + bookReturned.BookTitle + "\n" + 
			"Member: " + bookReturned.MemberName + "\n" + 
			"FinesDue: 0")
		if err := n.Notify(subject, body, bookReturned.MemberPhone); err != nil {
			fmt.Printf("Error sending notification to %v", bookReturned.MemberPhone)
		}
	}
	return nil
}