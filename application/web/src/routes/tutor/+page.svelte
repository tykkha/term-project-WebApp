<script lang="ts">
    // Var
    let isTutor = true;

    // interface Profile {
    //     photo: string;
    //     name: string;
    //     tags: string[]; 
    //     bio: string;
    // }

    // interface Session {
    //     sId: number;
    //     date: string;
    //     timeStart: string;
    //     timeEnd: string;
    //     location?: string;
    // }

    // interface Contacts {
    //     email: string;
    //     phone: number;
    // }

    // interface Review {
    //     rId: number;
    //     rating: number;
    //     feedback: string;
    // }

    // interface TutorData {
    //     profile: Profile;
    //     sessions: Session[]; 
    //     contacts: Contacts;
    //     reviews: Review[];
    // }
    
    // Temp mock data
    const tutorData = {
        profile: {
            name: "Jane Doe",
            photo: "https://grad.sfsu.edu/sites/default/files/images/new-student_2.jpg",
            tags: ["Computer Science", "Physics"],
            bio: "Hi, I'm Jane. My academic life is dedicated to two things: understanding how the universe works (Physics) and learning how to build powerful tools (Computer Science). I enjoy the challenge of bridging these two domains, constantly striving to use my technical skills to make sense of the world and contribute something new to it.",
        },
        sessions: [
            {
                sId: 1,
                date: "Tuesday, Nov 18th",
                timeStart: "14:00",
                timeEnd: "15:30",
                location: "J. Paul Leonard Library"
            },
            {
                sId: 2,
                date: "Thursday, Nov 20th",
                timeStart: "12:00",
                timeEnd: "13:00",
                location: "Cesar Chavez Student Center"
            },
            {
                sId: 3,
                date: "Friday, Nov 21st",
                timeStart: "10:00",
                timeEnd: "11:00",
                location: "Burk Hall"
            }
        ],
        contacts: {
            email: "mockstudent1@sfsu.edu",
            phone
            : "(123)456-7890",
        },
        reviews: [
            {
                rId: 1,
                studentName: "Alex R.",
                rating: 4.5,
                feedback: "Jane is an amazing tutor! She helped me understand complex Physics concepts easily. Highly recommend!",
            },
            {
                rId: 2,
                studentName: "Sam K.",
                rating: 4,
                feedback: "Great session on data structures. Jane is very patient and knowledgeable in Computer Science. A bit hard to book a time, but worth it.",
            },
            {
                rId: 3,
                studentName: "Taylor M.",
                rating: 5,
                feedback: "Excellent tutor for my introductory CS class. She clarified my code debugging issues very quickly!",
            }
        ]
    };

    const { profile, sessions, contacts, reviews } = tutorData;

    // Pull tutor profile
    function loadTutorPage () {
        
    }

    // Removes session from availability and adds to user session 
    function scheduleSession(sessionId: number) {
        alert(`Session added`);
    }
</script>

<!--Tutor page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
	<div class="mx-auto flex flex-col p-8 md:flex-row">

        <!--Tutor profile info col-->
		<div class="w-full p-4 md:w-4/12">
            <!--Tutor photo card-->
            <div class="mb-8 w-full rounded-2xl bg-white drop-shadow-lg transition duration-300 hover:scale-[1.02] hover:drop-shadow-2xl">
                <img src={profile.photo} alt="{profile.name} Profile Photo" class="w-full h-auto rounded-xl">
            </div>

            <!--Tutor name, tags, and bio card-->
            <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="mb-2 text-2xl underline text-center">{profile.name}</h2>
                <div class="flex flex-wrap justify-center gap-2">
                    {#each profile.tags as tag}
                        <span class="bg-[#231161] text-white text-sm px-2 py-1 rounded shadow-md">
                            {tag}
                        </span>
                    {/each}
                </div>
                <p class="p-3 text-base">{profile.bio}</p>
            </div>
        </div>

        <!--Available tutor sessions col-->
        <div class="w-full p-4 md:w-7/12">
            <h2 class="text-center mb-4 text-4xl underline">Available Tutoring Sessions</h2>
            <!--session card(s)-->
            {#each sessions as session (session.sId)}
                <div class="mx-auto flex flex-col mb-4 rounded-2xl bg-white p-4 drop-shadow-lg md:flex-row">
                    <div class="w-full md:w-9/12">
                        <p class="text-lg">Date: {session.date} </p>
                        <p class="text-lg">Time: {session.timeStart} to {session.timeEnd}</p>
                        <p class="text-lg">Location: {session.location}</p>
                    </div>
                    <div class="flex w-full justify-end items-end md:w-3/12">
                        <button 
                            class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"
                            on:click={() => scheduleSession(session.sId)}
                        > <!--TODO add schdule button function-->
                            Schedule
                        </button>
                    </div>
                </div>
            {/each}

            <!--Should only show in tutor view!!!!!-->
            {#if isTutor}
            <div class="flex justify-center">
                <a href="./tutor/session" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"> 
                    Add session
                </a>
            </div>
                
            {/if}
        </div>

        <!--Contacts & Reviews col-->
        <div class="w-full p-4 md:w-5/12">
            <!--Contacts card-->
            <div class="mb-8 w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="text-2xl underline text-center">Contacts</h2>
                <p class="text-lg">Email: {contacts.email}</p>
                <p class="text-lg">Phone: {contacts.phone}</p>
            </div>

            <!--User reviews card-->
            <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="mb-4 text-2xl underline text-center">Reviews</h2>
                {#each reviews as review (review.rId)}
                    <div class="mb-4 rounded-2xl p-3 shadow-sm">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-2xl bg-green-500 px-3 py-1">{review.rating}</span>
                            <span class="font-bold text-xl">{review.studentName}</span>
                        </div>
                        <div>
                            <p class="text-base italic">"{review.feedback}"</p>
                        </div>
                    </div>
                {/each}
                <div class="flex justify-center">
                    <a href="./tutor/review" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">
                        Leave a Review!
                    </a>
                </div>
                
            </div>
        </div>
    </div>
</div>