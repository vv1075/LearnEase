package main

type Quiz struct {
	ID          string     `json:"id"`
	Title       string     `json:"title"`
	CourseID    string     `json:"course_id"`
	Questions   []Question `json:"questions"`
	TotalMarks  int        `json:"total_marks"`
	LastUpdated int64      `json:"last_updated"`
	Status      string     `json:"status"` // "draft" or "saved"
	Source      string     `json:"source"` // "manual" or "ai"
}

type Question struct {
	ID      int      `json:"id"`
	Text    string   `json:"text"`
	Options []string `json:"options"`
	Correct int      `json:"correct"`
	Marks   int      `json:"marks"`
}

type Submission struct {
	QuizID  string `json:"quiz_id"`
	Answers []int  `json:"answers"`
}
