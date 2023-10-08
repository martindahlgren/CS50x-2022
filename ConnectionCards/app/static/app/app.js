function ProfileCard() {
    return (
      <div className="profilecard">
        Test Data!
      </div>
    );
}

function SwipeApp() {
    return (
        <div class="profile_view">
            <ProfileCard />
            <ProfileCard />
            <ProfileCard />
            <ProfileCard />
        </div>
    );
}

ReactDOM.render(<SwipeApp />, document.querySelector("#app"));