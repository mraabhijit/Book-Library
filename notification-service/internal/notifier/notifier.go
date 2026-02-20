package notifier

type Notifier interface {
	Notify(subject string, body string, recipient string) error
}