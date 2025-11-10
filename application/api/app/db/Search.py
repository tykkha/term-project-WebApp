from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from typing import List, Dict, Any

#Dependency: pip install sqlalchemy pymysql

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    uid = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    Type = Column(Enum('user', 'admin'))
    tutor = relationship("Tutor", back_populates="user", uselist=False)

class Tags(Base):
    __tablename__ = 'Tags'
    tagsID = Column(Integer, primary_key=True, autoincrement=True)
    tags = Column(String(8))

class Tutor(Base):
    __tablename__ = 'Tutor'
    tid = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey('User.uid', ondelete='CASCADE'), nullable=False)
    rating = Column(Float)
    user = relationship("User", back_populates="tutor")
    posts = relationship("Post", back_populates="tutor")

class Post(Base):
    __tablename__ = 'Posts'
    pid = Column(Integer, primary_key=True, autoincrement=True)
    tid = Column(Integer, ForeignKey('Tutor.tid', ondelete='CASCADE'), nullable=False)
    tags = Column(Integer, ForeignKey('Tags.tagsID', ondelete='CASCADE'), nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    tutor = relationship("Tutor", back_populates="posts")
    tag = relationship("Tags")

class Profile(Base):
    __tablename__ = 'Profile'
    profileID = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey('User.uid', ondelete='CASCADE'), nullable=False)
    tags = Column(Integer, ForeignKey('Tags.tagsID', ondelete='CASCADE'), nullable=False)
    status = Column(String(50))
    bio = Column(Text)
    user = relationship("User")
    tag = relationship("Tags")

class GatorGuidesSearch:
    def __init__(self, host: str, database: str, user: str, password: str):
        try:
            connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
            self.engine = create_engine(connection_string, echo=False)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            print("Successfully connected to GatorGuides database")
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            self.session = None

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not self.session:
            return []

        tutor_data = {}

        posts_by_tag = self.session.query(Post).join(Tags).filter(
            Tags.tags.like(f'%{query}%')
        ).order_by(Post.timestamp.desc()).all()

        for post in posts_by_tag:
            tid = post.tutor.tid
            if tid not in tutor_data:
                profile = self.session.query(Profile).filter(Profile.uid == post.tutor.uid).first()
                profile_tags = []
                profile_bio = None
                if profile:
                    all_profiles = self.session.query(Profile).filter(Profile.uid == post.tutor.uid).all()
                    profile_tags = list(set([p.tag.tags for p in all_profiles]))
                    profile_bio = profile.bio

                tutor_data[tid] = {
                    'tid': tid,
                    'name': f"{post.tutor.user.firstName} {post.tutor.user.lastName}",
                    'email': post.tutor.user.email,
                    'rating': post.tutor.rating,
                    'profile_tags': profile_tags,
                    'bio': profile_bio,
                    'priority': 1,
                    'match_type': 'tag',
                    'posts': [],
                    'courses': set()
                }

            tutor_data[tid]['posts'].append({
                'pid': post.pid,
                'course': post.tag.tags,
                'content': post.content,
                'timestamp': post.timestamp
            })
            tutor_data[tid]['courses'].add(post.tag.tags)

        tutors_by_name = self.session.query(Tutor).join(User).filter(
            (User.firstName.like(f'%{query}%')) |
            (User.lastName.like(f'%{query}%'))
        ).order_by(Tutor.rating.desc()).all()

        for tutor in tutors_by_name:
            if tutor.tid not in tutor_data:
                all_posts = self.session.query(Post).filter(
                    Post.tid == tutor.tid
                ).order_by(Post.timestamp.desc()).all()

                posts_list = [{
                    'pid': post.pid,
                    'course': post.tag.tags,
                    'content': post.content,
                    'timestamp': post.timestamp
                } for post in all_posts]

                profile = self.session.query(Profile).filter(Profile.uid == tutor.uid).first()
                profile_tags = []
                profile_bio = None
                if profile:
                    all_profiles = self.session.query(Profile).filter(Profile.uid == tutor.uid).all()
                    profile_tags = list(set([p.tag.tags for p in all_profiles]))
                    profile_bio = profile.bio

                tutor_data[tutor.tid] = {
                    'tid': tutor.tid,
                    'name': f"{tutor.user.firstName} {tutor.user.lastName}",
                    'email': tutor.user.email,
                    'rating': tutor.rating,
                    'profile_tags': profile_tags,
                    'bio': profile_bio,
                    'priority': 2,
                    'match_type': 'name',
                    'posts': posts_list,
                    'courses': set([post.tag.tags for post in all_posts])
                }

        results = []
        for tid, data in tutor_data.items():
            data['courses'] = list(data['courses'])
            results.append(data)

        results.sort(key=lambda x: (x['priority'], -x['rating'] if x['rating'] else 0))

        return results

    def close(self):
        if self.session:
            self.session.close()
            print("Database connection closed")

def print_results(results: List[Dict[str, Any]], query: str):
    print(f"\n{'=' * 70}")
    print(f"Search Results for '{query}' ({len(results)} tutors found)")
    print('=' * 70)

    if not results:
        print("No results found.")
        return

    tag_matches = [r for r in results if r['priority'] == 1]
    name_matches = [r for r in results if r['priority'] == 2]

    if tag_matches:
        print(f"\n{'─' * 70}")
        print(f"TAG MATCHES ({len(tag_matches)} tutors)")
        print('─' * 70)

        for i, tutor in enumerate(tag_matches, 1):
            print(f"\n{i}. {tutor['name']} (★{tutor['rating']})")
            print(f"   Email: {tutor['email']}")
            courses = ', '.join(tutor['courses'])
            print(f"   Courses: {courses}")
            if tutor['profile_tags']:
                profile_tags = ', '.join(tutor['profile_tags'])
                print(f"   Profile Tags: {profile_tags}")
            if tutor['bio']:
                print(f"   Bio: {tutor['bio']}")

            if tutor['posts']:
                print(f"   Posts ({len(tutor['posts'])}):")
                for j, post in enumerate(tutor['posts'], 1):
                    content = post['content'] or "No content"
                    print(f"      {j}. [{post['course']}]")
                    print(f"         {content}")
                    if j < len(tutor['posts']):
                        print()
            else:
                print(f"   No posts available")

    if name_matches:
        print(f"\n{'─' * 70}")
        print(f"NAME MATCHES ({len(name_matches)} tutors)")
        print('─' * 70)

        start_num = len(tag_matches) + 1
        for i, tutor in enumerate(name_matches, start_num):
            print(f"\n{i}. {tutor['name']} (★{tutor['rating']})")
            print(f"   Email: {tutor['email']}")
            courses = ', '.join(tutor['courses']) if tutor['courses'] else 'No courses'
            print(f"   Courses: {courses}")
            if tutor['profile_tags']:
                profile_tags = ', '.join(tutor['profile_tags'])
                print(f"   Profile Tags: {profile_tags}")
            if tutor['bio']:
                print(f"   Bio: {tutor['bio']}")

            if tutor['posts']:
                print(f"   Posts ({len(tutor['posts'])}):")
                for j, post in enumerate(tutor['posts'], 1):
                    content = post['content'] or "No content"
                    print(f"      {j}. [{post['course']}]")
                    print(f"         {content}")
                    if j < len(tutor['posts']):
                        print()
            else:
                print(f"   No posts available")

def main():
    print("GatorGuides Universal Search")
    print("-" * 60)

    host = input("Enter MySQL host (default: localhost:3663): ") or "localhost:3663"
    database = input("Enter database name (default: GatorGuides): ") or "GatorGuides"
    user = input("Enter MySQL username: ")
    password = input("Enter MySQL password: ")

    search = GatorGuidesSearch(host, database, user, password)

    if not search.session:
        print("Failed to connect to database. Exiting.")
        return

    print("\n" + "=" * 60)
    print("Universal Search - Just type anything to search!")
    print("Searches: Course tags, Tutor names")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:
        query = input("\nSearch: ").strip()

        if query.lower() == 'exit':
            print("\nExiting...")
            break

        if not query:
            print("Please enter a search term.")
            continue

        results = search.search(query)
        print_results(results, query)

    search.close()

if __name__ == "__main__":
    main()