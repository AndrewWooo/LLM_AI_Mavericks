package main

import (
	"bytes"
	"github.com/jarcoal/httpmock"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHandler(t *testing.T) {
	// Activate the httpmock
	httpmock.Activate()
	defer httpmock.DeactivateAndReset()

	// Mock the OpenAI API
	httpmock.RegisterResponder("POST", "https://api.openai.com/v1/chat/completions",
		httpmock.NewStringResponder(200, `{"id": "mock-id", "object": "mock-object", "created": 1620133500, "model": "gpt-3.5-turbo", "usage": {"prompt_tokens": 4, "completion_tokens": 6}, "choices": [{"message": {"role": "assistant", "content": "Mocked response from OpenAI API"}}]}`))

	// Initialize the request body
	reqBody := bytes.NewBuffer([]byte(`{"content":"test content"}`))
	req, err := http.NewRequest("POST", "/api", reqBody)
	if err != nil {
		t.Fatal(err)
	}

	// Create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response
	rr := httptest.NewRecorder()

	// Create a very simple fake OpenAI API key for testing
	fakeAPIKey := "fakeAPIKey"

	// Handler
	handler := handler(fakeAPIKey)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method directly and pass in our Request and ResponseRecorder
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	// Check the response body is what we expect.
	// This is a very basic check. In reality, you would probably want to do something more sophisticated,
	// like unmarshaling the response into a struct and checking the individual fields.
	expected := `{"response":"{\"id\": \"mock-id\", \"object\": \"mock-object\", \"created\": 1620133500, \"model\": \"gpt-3.5-turbo\", \"usage\": {\"prompt_tokens\": 4, \"completion_tokens\": 6}, \"choices\": [{\"message\": {\"role\": \"assistant\", \"content\": \"Mocked response from OpenAI API\"}}]}"}` // Replace this with the expected response
	got := strings.TrimSpace(rr.Body.String())
	want := strings.TrimSpace(expected)

	if got != want {
		t.Errorf("handler returned unexpected body: got %v want %v", got, want)
	}
}
