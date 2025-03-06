import streamlit as st
from weather_assistant import WeatherAssistant

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []  # Store query-response pairs
if "unit" not in st.session_state:
    st.session_state.unit = "metric"  # Default temperature unit: Celsius

def main():
    st.title("🌤 SkyWise – AI Weather Assistant")
    st.write("Ask about the weather in any city!")

    # Unit selection dropdown
    unit_options = {"Celsius": "metric", "Fahrenheit": "imperial"}
    selected_unit = st.selectbox(
        "Select Temperature Unit:",
        options=list(unit_options.keys()),
        index=0,  # Default to Celsius
    )
    st.session_state.unit = unit_options[selected_unit]  # Update session state with selected unit

    # User input field
    user_question = st.text_input("Enter your weather question:", "")

    # Toggle for enabling/disabling emojis
    use_emojis = st.checkbox("Enable Emojis in Responses", value=True)

    # Option to request customizable forecast
    forecast_days = st.slider("Select number of days for forecast (up to 5):", 1, 5, 1)

    # Display history of interactions
    st.subheader("Interaction History")
    for entry in st.session_state.history:
        st.markdown(f"**Query:** {entry['query']}")
        st.markdown(f"**Response:** {entry['response']}")
        st.markdown("---")

    if st.button("Get Weather"):
        if user_question:
            with st.spinner("Fetching weather..."):
                # Fetch weather information
                assistant = WeatherAssistant()
                if forecast_days > 1:
                    user_question += f" Provide a {forecast_days}-day forecast."
                response = assistant.ask_weather(user_question, use_emojis)

                # Save interaction to session state
                st.session_state.history.append({"query": user_question, "response": response})

                # Display the response
                st.markdown(f"**Response:** {response}")
        else:
            st.error("Please enter a question.")

if __name__ == "__main__":
    main()
