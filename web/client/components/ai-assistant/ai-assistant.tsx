import AIAssistantButton from "./ai-assistant-button"
import AIAssistantPanel from "./ai-assistant-panel"

/**
 * Main AI Assistant component that renders both the button and panel.
 * This should be included once at the app level to provide global access.
 */
export default function AIAssistant() {
  return (
    <>
      <AIAssistantButton />
      <AIAssistantPanel />
    </>
  )
}
