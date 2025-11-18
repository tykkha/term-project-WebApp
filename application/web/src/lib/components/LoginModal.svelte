<script lang="ts">
    import { X } from '@lucide/svelte';

    let { isOpen = $bindable(false), onLogin = (userData) => {} } = $props();

    let email = $state('');
    let password = $state('');
    let rememberMe = $state(false);
    let errorMessage = $state('');

    function handleLogin() {
        errorMessage = '';

        if (!email || !password) {
            errorMessage = 'Please enter both email and password';
            return;
        }

        if (!email.includes('@')) {
            errorMessage = 'Please enter a valid email address';
            return;
        }

        //left to add authentication logic
        console.log('Login attempt:', { email, password, rememberMe });

        //simulate successful login
        const mockUser = {
            name: 'John Doe',
            email: email,
            studentId: '920123456'
        };

        //call the onLogin callback passed from layout
        onLogin(mockUser);

        //close modal
        isOpen = false;

        //reset form
        email = '';
        password = '';
        errorMessage = '';
    }

    function handleClose() {
        isOpen = false;
        email = '';
        password = '';
        errorMessage = '';
    }

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            handleClose();
        }
    }
</script>

{#if isOpen}
    <div
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
            onclick={handleClose}
            onkeydown={handleKeyDown}
            role="button"
            tabindex="-1"
    >
        <div
                class="relative w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl mx-4"
                onclick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
                aria-labelledby="login-title"
        >
            <button
                    onclick={handleClose}
                    class="absolute right-4 top-4 rounded-full p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
                    aria-label="Close login modal"
            >
                <X size={24} />
            </button>

            <h2 id="login-title" class="mb-6 text-3xl font-bold text-[#231161]">Welcome Back</h2>

            <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }}>
                <div class="mb-4">
                    <label for="email" class="mb-2 block text-sm font-medium text-gray-700">
                        Email Address
                    </label>
                    <input
                            id="email"
                            type="email"
                            bind:value={email}
                            placeholder="you@example.com"
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
                    />
                </div>

                <div class="mb-4">
                    <label for="password" class="mb-2 block text-sm font-medium text-gray-700">
                        Password
                    </label>
                    <input
                            id="password"
                            type="password"
                            bind:value={password}
                            placeholder="••••••••"
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
                    />
                </div>

                {#if errorMessage}
                    <div class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                        {errorMessage}
                    </div>
                {/if}

                <div class="mb-6 flex items-center justify-between">
                    <label class="flex items-center">
                        <input
                                type="checkbox"
                                bind:checked={rememberMe}
                                class="mr-2 h-4 w-4 rounded border-gray-300 text-[#231161] focus:ring-[#231161]"
                        />
                        <span class="text-sm text-gray-700">Remember me</span>
                    </label>
                    <a href="/forgot-password" class="text-sm text-[#231161] hover:underline">
                        Forgot password?
                    </a>
                </div>

                <button
                        type="submit"
                        class="w-full rounded-lg bg-[#231161] px-4 py-3 font-semibold text-white transition-colors hover:bg-[#1a0d4a] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-offset-2"
                >
                    Sign In
                </button>

                <div class="mt-6 text-center">
                    <p class="text-sm text-gray-600">
                        Don't have an account?
                        <a href="/register" class="font-medium text-[#231161] hover:underline">Sign up</a>
                    </p>
                </div>
            </form>
        </div>
    </div>
{/if}