<template>
  <div class="min-h-screen bg-gray-100 flex flex-col">
    <!-- Header -->
    <header class="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
      <h1 class="text-xl font-bold">Crypto Chat Assistant</h1>
      <button @click="toggleSpeaker" 
              class="p-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
              :class="{'text-white': isSpeakerOn, 'text-gray-300': !isSpeakerOn}">
        <svg v-if="isSpeakerOn" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.728-2.728" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15.536a5 5 0 010-7.072m2.828 9.9a9 9 0 010-12.728M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4l16 16" />
        </svg>
      </button>
    </header>

    <!-- Chat Container -->
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index"
             :class="['flex', message.isUser ? 'justify-end' : 'justify-start']">
          <div :class="['max-w-[80%] rounded-lg p-3',
                       message.isUser ? 'bg-blue-500 text-white' : 'bg-white text-gray-800']">
            <div v-if="typeof message.content === 'string'" 
                 class="message-content whitespace-pre-line break-words" 
                 v-html="formatMessage(message.content)"></div>
            <div v-else-if="message.content.type === 'chart'" class="w-full h-64">
              <Line :data="message.content.data" :options="message.content.options" />
            </div>
            <div class="text-xs mt-1 opacity-75">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-white rounded-lg p-3 text-gray-800">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t bg-white p-4">
        <div class="flex space-x-2">
          <button @click="toggleVoiceInput" 
                  class="p-2 rounded-full hover:bg-gray-100"
                  :class="{'text-red-500': isRecording}">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
          <input v-model="userInput" 
                 @keyup.enter="sendMessage"
                 type="text"
                 placeholder="Try: 'Show me ETH stats' or 'Show BTC chart'..."
                 class="flex-1 border rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
          <button @click="sendMessage"
                  class="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600">
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default {
  name: 'App',
  components: {
    Line
  },
  setup() {
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const isRecording = ref(false)
    const isSpeakerOn = ref(true)
    const messagesContainer = ref(null)
    const recognition = ref(null)

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
      recognition.value = new webkitSpeechRecognition()
      recognition.value.continuous = false
      recognition.value.interimResults = false
      recognition.value.lang = 'en-US'

      recognition.value.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        userInput.value = transcript
        sendMessage()
      }

      recognition.value.onend = () => {
        isRecording.value = false
      }
    }

    const toggleVoiceInput = () => {
      if (isRecording.value) {
        recognition.value.stop()
      } else {
        recognition.value.start()
        isRecording.value = true
      }
    }

    const toggleSpeaker = () => {
      isSpeakerOn.value = !isSpeakerOn.value
      if (!isSpeakerOn.value) {
        window.speechSynthesis.cancel()
      }
    }

    const speak = (text) => {
      if (!isSpeakerOn.value) return
      const utterance = new SpeechSynthesisUtterance(text)
      window.speechSynthesis.speak(utterance)
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const formatMessage = (content) => {
      if (typeof content === 'string') {
        // Convert newlines to <br> tags for proper display
        return content.replace(/\n/g, '<br>')
      }
      return content
    }

    const scrollToBottom = async () => {
      await nextTick()
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const processUserMessage = async (message) => {
      const lowerMessage = message.toLowerCase()
      
      if (lowerMessage.includes('price') || lowerMessage.includes('trading')) {
        const symbol = message.match(/\b[A-Z]{2,}\b/)?.[0] || 'BTC'
        try {
          const response = await axios.get(`http://localhost:8000/api/price/${symbol}`)
          return `The current price of ${symbol} is $${response.data.price.toLocaleString()}`
        } catch (error) {
          return `Sorry, I couldn't fetch the price for ${symbol}. Please try again later.`
        }
      }

      if (lowerMessage.includes('trending')) {
        try {
          const response = await axios.get('http://localhost:8000/api/trending')
          const coins = response.data.coins.slice(0, 5)
          return `Here are the top trending coins:\n${coins.map(coin => 
            `- ${coin.item.name} (${coin.item.symbol.toUpperCase()})`
          ).join('\n')}`
        } catch (error) {
          return 'Sorry, I couldn\'t fetch trending coins. Please try again later.'
        }
      }

      if (lowerMessage.includes('stats') || lowerMessage.includes('info') || lowerMessage.includes('show me')) {
        const symbol = message.match(/\b[A-Z]{2,}\b/)?.[0] || 'BTC'
        try {
          const response = await axios.get(`http://localhost:8000/api/stats/${symbol}`)
          const data = response.data
          return `📊 ${data.name} (${data.symbol}) Statistics:\n\n` +
                 `💰 Market Cap: $${data.market_cap.toLocaleString()}\n` +
                 `📈 24h Change: ${data.price_change_24h.toFixed(2)}%\n\n` +
                 `📝 Description:\n${data.description}`
        } catch (error) {
          return `Sorry, I couldn't fetch stats for ${symbol}. Please try again later.`
        }
      }

      if (lowerMessage.includes('chart') || lowerMessage.includes('graph') || lowerMessage.includes('price history')) {
        const symbol = message.match(/\b[A-Z]{2,}\b/)?.[0] || 'BTC'
        try {
          const response = await axios.get(`http://localhost:8000/api/chart/${symbol}`)
          const prices = response.data.prices
          
          if (!prices || prices.length < 2) {
            return `Sorry, there isn't enough price data available for ${symbol}.`
          }
          
          const labels = prices.map(p => new Date(p[0]).toLocaleDateString())
          const data = prices.map(p => p[1])
          
          // Calculate min and max for better chart scaling
          const minPrice = Math.min(...data) * 0.99
          const maxPrice = Math.max(...data) * 1.01
          
          return {
            type: 'chart',
            data: {
              labels,
              datasets: [{
                label: `${symbol} Price (USD)`,
                data,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: true,
                  position: 'top'
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                  callbacks: {
                    label: (context) => {
                      const value = context.raw
                      return `${symbol}: $${value.toLocaleString()}`
                    }
                  }
                }
              },
              scales: {
                y: {
                  min: minPrice,
                  max: maxPrice,
                  ticks: {
                    callback: (value) => `$${value.toLocaleString()}`
                  }
                }
              }
            }
          }
        } catch (error) {
          console.error('Chart error:', error)
          if (error.response?.status === 404) {
            return `Sorry, I couldn't find price data for ${symbol}. Please try another cryptocurrency.`
          }
          return `Sorry, I couldn't fetch the chart for ${symbol}. Please try again later.`
        }
      }

      if (lowerMessage.includes('have') || lowerMessage.includes('holding') || lowerMessage.includes('add')) {
        const match = message.match(/(\d+(?:\.\d+)?)\s+([A-Z]{2,})/i) || 
                     message.match(/([A-Z]{2,})\s+(\d+(?:\.\d+)?)/i)
        if (match) {
          let amount, symbol;
          if (match[1].match(/^\d/)) {
            amount = match[1];
            symbol = match[2];
          } else {
            symbol = match[1];
            amount = match[2];
          }
          try {
            await axios.post('http://localhost:8000/api/portfolio', {
              symbol: symbol.toUpperCase(),
              amount: parseFloat(amount)
            })
            return `I've added ${amount} ${symbol.toUpperCase()} to your portfolio.`
          } catch (error) {
            console.error('Portfolio update error:', error);
            return 'Sorry, I couldn\'t update your portfolio. Please try again later.'
          }
        }
      }

      if (lowerMessage.includes('portfolio') || lowerMessage.includes('holdings')) {
        if (lowerMessage.includes('clear') || lowerMessage.includes('delete') || lowerMessage.includes('remove')) {
          try {
            await axios.delete('http://localhost:8000/api/portfolio')
            return 'Your portfolio has been cleared successfully.'
          } catch (error) {
            console.error('Portfolio clear error:', error)
            return 'Sorry, I couldn\'t clear your portfolio. Please try again later.'
          }
        }
        
        try {
          const response = await axios.get('http://localhost:8000/api/portfolio')
          const data = response.data
          return `Your portfolio value: $${data.total_value.toLocaleString()}\n` +
                 `Holdings:\n${data.holdings.map(h => 
                   `- ${h.amount} ${h.symbol}: $${h.value.toLocaleString()}`
                 ).join('\n')}`
        } catch (error) {
          return 'Sorry, I couldn\'t fetch your portfolio. Please try again later.'
        }
      }

      return "I'm not sure how to help with that. You can ask me about:\n" +
             "- Current crypto prices\n" +
             "- Trending coins\n" +
             "- Coin statistics\n" +
             "- 7-day price charts\n" +
             "- Your portfolio"
    }

    const sendMessage = async () => {
      if (!userInput.value.trim()) return

      const userMessage = userInput.value
      messages.value.push({
        content: userMessage,
        isUser: true,
        timestamp: new Date()
      })
      userInput.value = ''
      await scrollToBottom()

      isLoading.value = true
      const response = await processUserMessage(userMessage)
      isLoading.value = false

      messages.value.push({
        content: response,
        isUser: false,
        timestamp: new Date()
      })
      await scrollToBottom()

      if (typeof response === 'string') {
        speak(response)
      }
    }

    onMounted(() => {
      messages.value.push({
        content: "Hello! I'm your crypto assistant. How can I help you today?",
        isUser: false,
        timestamp: new Date()
      })
      speak("Hello! I'm your crypto assistant. How can I help you today?")
    })

    return {
      messages,
      userInput,
      isLoading,
      isRecording,
      isSpeakerOn,
      messagesContainer,
      sendMessage,
      toggleVoiceInput,
      toggleSpeaker,
      formatTime,
      formatMessage
    }
  }
}
</script>

<style>
.animate-bounce {
  animation: bounce 1s infinite;
}

.delay-100 {
  animation-delay: 100ms;
}

.delay-200 {
  animation-delay: 200ms;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-25%);
  }
}

/* Add styles for better message formatting */
.message-content {
  line-height: 1.5;
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

.message-content br {
  margin-bottom: 0.5rem;
  display: block;
  content: "";
}

/* Ensure proper spacing between paragraphs */
.message-content p {
  margin-bottom: 1rem;
}

/* Style for code blocks if needed */
.message-content pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.5rem;
  border-radius: 0.25rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

/* Add styles for the speaker button */
.text-blue-500 {
  color: #3B82F6;
}

button:focus {
  outline: none;
  ring: 2px;
  ring-color: #3B82F6;
}
</style> 