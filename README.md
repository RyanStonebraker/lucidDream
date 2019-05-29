# lucidDream
Three dimensional, emotionally-based AI character models applied to dynamic story telling.

## Development Stages
1. Establish word vector interpretation system for defining key parts of response
  - Ex. ("good", "weather", "tomorrow") -> "The weather looks good for tomorrow."
  - Use GAN architecture to interpolate word vectors to full sentences
2. Generate meaningful word vectors based on probability queue
  - Create list of topics that have an assigned probability for the response to be about
  - Each topic also has a list of adjectives that have a probability of being selected
  - Length of response should be determined by specificity rating of question (ex. "why?" is open ended, "what time is it?" is not)
3. Build 3 dimensional emotion models by using a clustering approach to evaluate specific written work by individual authors
  - These emotion models should impactt the probability queue word choices
4. Add in LSTM model to give historical value to previous responses
5. Assign physical constraints to model ("health", "height", etc.)
6. Have first-person verbs correspond to actions that must take into account physical constraints when being a part of responses
7. Add in environment
  - Conditions in environment influence responses
  - User can influence environmental conditions
8. Have responses over time impact emotion model
9. Add multiple character models to shared environment
10. Record interactions and actions to create story
