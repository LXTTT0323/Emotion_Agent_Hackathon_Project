## MVP Goals

1. Accept user text input and (mocked or real) health data from iOS app
2. Perform emotion classification on the input text
3. Match against user profile and context memory (e.g. recent emotions)
4. Generate a gentle, personalized suggestion using Semantic Kernel and prompt template
5. Return suggestion to frontend and display it
6. Save interaction history to local memory

### Phase 1 Goals (April 12–14)
- [x] Define core API endpoints and prompt templates
- [x] Build FastAPI skeleton with mock tools
- [x] SwiftUI interface with Apple HealthKit fetch logic (mock OK)
- [x] Agent suggests intervention based on emotion + HRV
- [ ] Record simple demo video

### Phase 2 Goals (April 15–21)
- [ ] Implement real emotion classification using NLP model
- [ ] Create user profiles with preferences
- [ ] Improve suggestion generation with richer templates
- [ ] Add proper error handling and edge cases
- [ ] Build memory system for context awareness

### Phase 3 Goals (April 22–30)
- [ ] Integrate real HealthKit data
- [ ] Improve UI with emotion history visualization
- [ ] Add notification system for interventions
- [ ] Implement user feedback mechanism
- [ ] Performance optimization and testing

### Flow Summary
User input + Health data → Backend `/analyze` → Semantic Kernel agent uses tools → Generates suggestion → iOS displays it → memory.json logs interaction

### Open Questions

1. How should we handle offline mode when backend is unavailable?
2. What's the optimal refresh rate for health data collection?
3. How do we balance proactive notifications vs user privacy?
4. What's the best way to store sensitive health data securely?

### Success Metrics

1. User engagement: Average interactions per day
2. Emotional improvement: Positive trend in emotion classification over time
3. Suggestion relevance: User feedback on suggestion quality
4. Technical performance: Response time under 1 second 