package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
)

type Input struct {
	Content string `json:"content"`
}

type Output struct {
	Response string `json:"response"`
}

func handler(apiKey string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Parse the JSON body
		var input Input
		err := json.NewDecoder(r.Body).Decode(&input)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// Call OpenAI API
		url := "https://api.openai.com/v1/chat/completions"
		payload := strings.NewReader(fmt.Sprintf(`{
		"model": "gpt-3.5-turbo",
		"messages": [{"role": "user", "content": "%s"}],
		"temperature": 0.7
	}`, input.Content))

		req, _ := http.NewRequest("POST", url, payload)
		req.Header.Add("Content-Type", "application/json")
		req.Header.Add("Authorization", "Bearer "+apiKey)

		res, _ := http.DefaultClient.Do(req)
		defer res.Body.Close()
		body, _ := ioutil.ReadAll(res.Body)

		// Format and send the response
		var response Output
		response.Response = string(body)
		json.NewEncoder(w).Encode(response)
	}
}

func main() {
	// Read the API key from api-key.txt
	apiKeyBytes, err := ioutil.ReadFile("./api-key.txt")
	if err != nil {
		fmt.Println("Error reading API key:", err)
		os.Exit(1)
	}
	apiKey := strings.TrimSpace(string(apiKeyBytes))

	http.HandleFunc("/api", handler(apiKey))
	http.ListenAndServe(":8080", nil)
}
