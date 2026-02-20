package models

type BookCreatedEvent struct {
	Event 		string 	`json:"event"`
	BookID 		int 	`json:"book_id"`
	Title 		string 	`json:"title"`
	Author 		string 	`json:"author"`
	Description string 	`json:"description"`
}

type BookBorrowedEvent struct {
	Event        string `json:"event"`
	BookID       int    `json:"book_id"`
	MemberID     int    `json:"member_id"`
	BookTitle    string `json:"book_title"`
	MemberName   string `json:"member_name"`
	MemberPhone  string `json:"member_phone"`
	BorrowedDate string `json:"borrowed_date"`
	DueDate      string `json:"due_date"`
}

type BookReturnedEvent struct {
	Event        string `json:"event"`
	BookID       int    `json:"book_id"`
	MemberID     int    `json:"member_id"`
	BookTitle    string `json:"book_title"`
	MemberName   string `json:"member_name"`
	MemberPhone  string `json:"member_phone"`
	BorrowedDate string `json:"borrowed_date"`
	DueDate      string `json:"due_date"`
	ReturnedDate string `json:"returned_date"`
}