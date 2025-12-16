<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import {
		getRecentConversations,
		getConversation,
		sendMessage,
		createWebSocket,
		getCurrentUser,
		getSessionID,
		type Conversation,
		type Message
	} from '$lib/api';

	let conversations: Conversation[] = [];
	let selectedConversation: Conversation | null = null;
	let messages: Message[] = [];
	let messageInput = '';
	let ws: WebSocket | null = null;
	let currentUser = getCurrentUser();
	let loading = false;
	let error = '';
	let messagesContainer: HTMLDivElement;
	let keepaliveInterval: number | null = null;

	onMount(async () => {
		if (!currentUser) {
			error = 'Please log in to access messages';
			return;
		}
		
		// Connect WebSocket immediately when page loads
		connectWebSocket();
		
		// Load conversations
		await loadConversations();
		
		// Start keepalive ping every 30 seconds
		keepaliveInterval = setInterval(() => {
			if (ws && ws.readyState === WebSocket.OPEN) {
				ws.send('ping');
			}
		}, 30000);
	});

	onDestroy(() => {
		// Clear keepalive interval
		if (keepaliveInterval) {
			clearInterval(keepaliveInterval);
		}
		
		// Close WebSocket when page is closed/navigated away
		closeWebSocket();
	});

	async function loadConversations() {
		if (!currentUser) return;
		try {
			loading = true;
			error = '';
			conversations = await getRecentConversations(currentUser.uid, 10);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load conversations';
		} finally {
			loading = false;
		}
	}

	async function selectConversation(conv: Conversation) {
		if (!currentUser) return;

		selectedConversation = conv;
		messages = [];
		error = '';

		try {
			loading = true;
			// Load last 30 messages
			messages = await getConversation(currentUser.uid, conv.otherUID, 30);
			
			// Scroll to bottom after messages load
			setTimeout(scrollToBottom, 100);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load conversation';
		} finally {
			loading = false;
		}
	}

	function connectWebSocket() {
		if (!currentUser || ws) return;

		const sessionID = getSessionID();
		if (!sessionID) {
			error = 'Authentication required';
			console.error('No session ID found');
			return;
		}

		try {
			console.log('Attempting WebSocket connection for user:', currentUser.uid);
			console.log('Session ID:', sessionID);
			
			ws = createWebSocket(currentUser.uid, sessionID);
			
			console.log('WebSocket created, readyState:', ws.readyState);

			ws.onopen = () => {
				console.log('✅ WebSocket connected successfully');
				error = ''; // Clear any connection errors
			};

			ws.onmessage = (event) => {
				try {
					// Handle pong response from keepalive
					if (event.data === 'pong') {
						console.log('Received pong');
						return;
					}
					
					console.log('Received message:', event.data);
					const message: Message = JSON.parse(event.data);
					
					// Add message if it's part of the current conversation
					if (
						selectedConversation &&
						((message.senderUID === selectedConversation.otherUID &&
							message.receiverUID === currentUser!.uid) ||
							(message.senderUID === currentUser!.uid &&
								message.receiverUID === selectedConversation.otherUID))
					) {
						messages = [...messages, message];
						setTimeout(scrollToBottom, 50);
					}
					
					// Update conversation list to reflect new message
					loadConversations();
				} catch (e) {
					console.error('Failed to parse message:', e);
				}
			};

			ws.onerror = (event) => {
				console.error('❌ WebSocket error:', event);
				console.error('WebSocket readyState:', ws?.readyState);
				console.error('Error type:', event.type);
				error = 'Connection error - check console for details';
			};

			ws.onclose = (event) => {
				console.log('WebSocket closed - Code:', event.code, 'Reason:', event.reason, 'Clean:', event.wasClean);
				ws = null;
				
				// Attempt to reconnect after 3 seconds if not intentionally closed
				if (event.code !== 1000 && currentUser) {
					console.log('Will attempt to reconnect in 3 seconds...');
					setTimeout(() => {
						console.log('Attempting to reconnect WebSocket...');
						connectWebSocket();
					}, 3000);
				}
			};
		} catch (e) {
			error = 'Failed to connect to chat server';
			console.error('WebSocket connection error:', e);
		}
	}

	function closeWebSocket() {
		if (ws) {
			ws.close(1000, 'User navigated away'); // Normal closure
			ws = null;
		}
	}

	function closeConversation() {
		selectedConversation = null;
		messages = [];
		error = '';
		// Keep WebSocket connected
	}

	async function handleSendMessage() {
		if (!currentUser || !selectedConversation || !messageInput.trim()) return;

		const content = messageInput.trim();
		messageInput = '';

		try {
			const message = await sendMessage({
				senderUID: currentUser.uid,
				receiverUID: selectedConversation.otherUID,
				content
			});

			// Add message to local state
			messages = [...messages, message];
			setTimeout(scrollToBottom, 50);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to send message';
			messageInput = content; // Restore message on error
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSendMessage();
		}
	}

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function formatTime(timestamp: string): string {
		const date = new Date(timestamp);
		return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
	}

	function formatDate(timestamp: string): string {
		const date = new Date(timestamp);
		const today = new Date();
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);

		if (date.toDateString() === today.toDateString()) {
			return 'Today';
		} else if (date.toDateString() === yesterday.toDateString()) {
			return 'Yesterday';
		} else {
			return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		}
	}
</script>

<div class="chat-container">
	<!-- Left Sidebar: Conversations List -->
	<div class="conversations-sidebar">
		<div class="sidebar-header">
			<h2>Messages</h2>
			{#if ws}
				<span class="connection-status connected" title="Connected">●</span>
			{:else}
				<span class="connection-status disconnected" title="Disconnected">●</span>
			{/if}
		</div>

		{#if loading && conversations.length === 0}
			<div class="loading">Loading conversations...</div>
		{:else if conversations.length === 0}
			<div class="empty-state">
				<p>No conversations yet</p>
				<p class="hint">Schedule a session with a tutor to start messaging</p>
			</div>
		{:else}
			<div class="conversations-list">
				{#each conversations as conv}
					<button
						class="conversation-item"
						class:active={selectedConversation?.otherUID === conv.otherUID}
						on:click={() => selectConversation(conv)}
					>
						<div class="conversation-avatar">
							{conv.otherName.charAt(0).toUpperCase()}
						</div>
						<div class="conversation-info">
							<div class="conversation-name">{conv.otherName}</div>
							<div class="conversation-preview">{conv.lastMessage}</div>
						</div>
						<div class="conversation-time">
							{formatDate(conv.lastMessageTime)}
						</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Right Panel: Chat Interface -->
	<div class="chat-panel">
		{#if !selectedConversation}
			<div class="empty-chat">
				<p>Select a conversation to start messaging</p>
			</div>
		{:else}
			<!-- Chat Header -->
			<div class="chat-header">
				<div class="chat-header-info">
					<div class="chat-avatar">
						{selectedConversation.otherName.charAt(0).toUpperCase()}
					</div>
					<h3>{selectedConversation.otherName}</h3>
				</div>
				<button class="close-btn" on:click={closeConversation}>&times;</button>
			</div>

			<!-- Messages Area -->
			<div class="messages-container" bind:this={messagesContainer}>
				{#if loading && messages.length === 0}
					<div class="loading-messages">Loading messages...</div>
				{:else if messages.length === 0}
					<div class="no-messages">
						<p>No messages yet</p>
						<p class="hint">Start the conversation!</p>
					</div>
				{:else}
					{#each messages as message}
						<div
							class="message"
							class:sent={message.senderUID === currentUser?.uid}
							class:received={message.senderUID !== currentUser?.uid}
						>
							<div class="message-content">
								<div class="message-text">{message.content}</div>
								<div class="message-time">{formatTime(message.timestamp)}</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>

			<!-- Error Display -->
			{#if error}
				<div class="error-banner">{error}</div>
			{/if}

			<!-- Message Input -->
			<div class="message-input-container">
				<input
					type="text"
					class="message-input"
					placeholder="Type a message..."
					bind:value={messageInput}
					on:keypress={handleKeyPress}
					disabled={loading || !ws}
				/>
				<button
					class="send-btn"
					on:click={handleSendMessage}
					disabled={!messageInput.trim() || loading || !ws}
				>
					Send
				</button>
			</div>
		{/if}
	</div>
</div>

<style>
	.chat-container {
		display: flex;
		height: 100vh;
		background: #f5f5f5;
	}

	/* Conversations Sidebar */
	.conversations-sidebar {
		width: 320px;
		background: white;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
	}

	.sidebar-header {
		padding: 20px;
		border-bottom: 1px solid #e0e0e0;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.sidebar-header h2 {
		margin: 0;
		font-size: 24px;
		font-weight: 600;
	}

	.connection-status {
		font-size: 12px;
		display: inline-block;
	}

	.connection-status.connected {
		color: #4caf50;
	}

	.connection-status.disconnected {
		color: #f44336;
	}

	.conversations-list {
		overflow-y: auto;
		flex: 1;
	}

	.conversation-item {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 20px;
		border: none;
		background: white;
		cursor: pointer;
		transition: background 0.2s;
		text-align: left;
		border-bottom: 1px solid #f0f0f0;
	}

	.conversation-item:hover {
		background: #f8f8f8;
	}

	.conversation-item.active {
		background: #e3f2fd;
	}

	.conversation-avatar {
		width: 48px;
		height: 48px;
		border-radius: 50%;
		background: #1976d2;
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 20px;
		font-weight: 600;
		flex-shrink: 0;
	}

	.conversation-info {
		flex: 1;
		min-width: 0;
	}

	.conversation-name {
		font-weight: 600;
		margin-bottom: 4px;
		color: #333;
	}

	.conversation-preview {
		font-size: 14px;
		color: #666;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.conversation-time {
		font-size: 12px;
		color: #999;
		flex-shrink: 0;
	}

	/* Chat Panel */
	.chat-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		background: white;
	}

	.chat-header {
		padding: 16px 20px;
		border-bottom: 1px solid #e0e0e0;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.chat-header-info {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.chat-avatar {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: #1976d2;
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
		font-weight: 600;
	}

	.chat-header h3 {
		margin: 0;
		font-size: 18px;
		font-weight: 600;
	}

	.close-btn {
		width: 32px;
		height: 32px;
		border: none;
		background: #f0f0f0;
		border-radius: 50%;
		font-size: 24px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #666;
		transition: background 0.2s;
	}

	.close-btn:hover {
		background: #e0e0e0;
	}

	.messages-container {
		flex: 1;
		overflow-y: auto;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 12px;
		background: #fafafa;
	}

	.message {
		display: flex;
		max-width: 70%;
	}

	.message.sent {
		align-self: flex-end;
	}

	.message.received {
		align-self: flex-start;
	}

	.message-content {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.message-text {
		padding: 10px 14px;
		border-radius: 12px;
		word-wrap: break-word;
	}

	.message.sent .message-text {
		background: #1976d2;
		color: white;
		border-bottom-right-radius: 4px;
	}

	.message.received .message-text {
		background: white;
		color: #333;
		border: 1px solid #e0e0e0;
		border-bottom-left-radius: 4px;
	}

	.message-time {
		font-size: 11px;
		color: #999;
		padding: 0 4px;
	}

	.message.sent .message-time {
		text-align: right;
	}

	.message-input-container {
		padding: 16px 20px;
		border-top: 1px solid #e0e0e0;
		display: flex;
		gap: 12px;
		background: white;
	}

	.message-input {
		flex: 1;
		padding: 10px 14px;
		border: 1px solid #e0e0e0;
		border-radius: 20px;
		font-size: 14px;
		outline: none;
		transition: border-color 0.2s;
	}

	.message-input:focus {
		border-color: #1976d2;
	}

	.message-input:disabled {
		background: #f5f5f5;
		cursor: not-allowed;
	}

	.send-btn {
		padding: 10px 24px;
		background: #1976d2;
		color: white;
		border: none;
		border-radius: 20px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.send-btn:hover:not(:disabled) {
		background: #1565c0;
	}

	.send-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	/* Empty States */
	.empty-state,
	.empty-chat,
	.no-messages {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: #999;
		text-align: center;
	}

	.empty-state p,
	.empty-chat p,
	.no-messages p {
		margin: 8px 0;
	}

	.hint {
		font-size: 14px;
		color: #bbb;
	}

	.loading,
	.loading-messages {
		text-align: center;
		padding: 40px;
		color: #999;
	}

	.error-banner {
		background: #ffebee;
		color: #c62828;
		padding: 12px 20px;
		text-align: center;
		font-size: 14px;
	}
</style>