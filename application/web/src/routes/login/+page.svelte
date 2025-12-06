<script lang="ts">
    import { goto } from '$app/navigation';
    import { loginUser } from '$lib/api';

    let email = $state('');
    let password = $state('');
    let rememberMe = $state(false);
    let errorMessage = $state('');
    let isLoggingIn = $state(false);

    async function handleLogin() {
        errorMessage = '';

        if (!email || !password) {
            errorMessage = 'Please enter both email and password';
            return;
        }

        if (!email.includes('@')) {
            errorMessage = 'Please enter a valid email address';
            return;
        }

        isLoggingIn = true;

        try {
            // Call backend login API
            await loginUser(email, password);

            // loginUser automatically saves session to localStorage
            // Redirect to dashboard (will route to student or tutor dashboard)
            goto('/dashboard');
        } catch (err: any) {
            console.error('Login error:', err);
            errorMessage = err?.message || 'Invalid email or password. Please try again.';
        } finally {
            isLoggingIn = false;
        }
    }
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-100 px-4 py-12">
    <div class="w-full max-w-md">
        <!--header-->
        <div class="mb-8 text-center">
            <h1 class="mb-2 text-4xl font-bold text-[#231161]">Gator Guides</h1>
            <p class="text-gray-600">Sign in to your account</p>
        </div>

        <!--Login form card-->
        <div class="rounded-2xl bg-white p-8 shadow-lg">
            <h2 class="mb-6 text-2xl font-bold text-[#231161]">Welcome Back</h2>

            <form
                    onsubmit={(e) => {
                    e.preventDefault();
                    handleLogin();
                }}
            >
                <div class="mb-4">
                    <label for="email" class="mb-2 block text-sm font-medium text-gray-700">
                        Email Address
                    </label>
                    <input
                            id="email"
                            type="email"
                            bind:value={email}
                            placeholder="you@sfsu.edu"
                            disabled={isLoggingIn}
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
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
                            disabled={isLoggingIn}
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                    />
                </div>

                {#if errorMessage}
                    <div class="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                        {errorMessage}
                    </div>
                {/if}

                <div class="mb-6 flex items-center justify-between">
                    <label class="flex items-center">
                        <input
                                type="checkbox"
                                bind:checked={rememberMe}
                                disabled={isLoggingIn}
                                class="mr-2 h-4 w-4 rounded border-gray-300 text-[#231161] focus:ring-[#231161] disabled:cursor-not-allowed"
                        />
                        <span class="text-sm text-gray-700">Remember me</span>
                    </label>
                    <a href="/forgot-password" class="text-sm text-[#231161] hover:underline">
                        Forgot password?
                    </a>
                </div>

                <button
                        type="submit"
                        disabled={isLoggingIn}
                        class="w-full rounded-lg bg-[#231161] px-4 py-3 font-semibold text-white transition-colors hover:bg-[#1a0d4a] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-offset-2 disabled:bg-[#231161]/60 disabled:cursor-not-allowed"
                >
                    {#if isLoggingIn}
                        Signing in...
                    {:else}
                        Sign In
                    {/if}
                </button>

                <div class="mt-6 text-center">
                    <p class="text-sm text-gray-600">
                        Don't have an account?
                        <a href="/student-register" class="font-medium text-[#231161] hover:underline">Sign up as student</a>
                        or
                        <a href="/tutor-register" class="font-medium text-[#231161] hover:underline">tutor</a>
                    </p>
                </div>

                <div class="mt-4 text-center">
                    <a href="/" class="text-sm text-gray-600 hover:text-gray-800">← Back to home</a>
                </div>
            </form>
        </div>

        <!--additional info-->
        <div class="mt-6 text-center text-sm text-gray-600">
            <p>
                Need help? <a href="/support" class="text-[#231161] hover:underline">Contact support</a>
            </p>
        </div>
    </div>
</div>