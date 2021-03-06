import React from 'react';
import Waiting from './Waiting';
import WaitingRoom from './WaitingRoom';
import Register from './Register';
import Login from './Login';
import base from '../base.js';
import { Button, Grid, Col, Alert} from 'react-bootstrap';
import { Link } from 'react-router';
import Modal from 'react-modal';
import signincss from '../css/signin.css';
//import '../css/music.css';
import {Privacy} from './Privacy'

class App extends React.Component {

    constructor() {
        super();
        this.saySend = this.saySend.bind(this);
        this.onLogout = this.onLogout.bind(this);
        this.checkUserVerified = this.checkUserVerified.bind(this);
        this.removeCurrentUserFromPeople = this.removeCurrentUserFromPeople.bind(this);
        this.addCurrentUserToPeople = this.addCurrentUserToPeople.bind(this);

        this.state = {
            people: [],
            user: {},
            invites: [],
            loggedIn: false,
            modalIsOpen: false,
            modal2IsOpen: false,
            modal3IsOpen: false,
            emailVerified: true
        };

        fetch('https://perfect-practice-dev.herokuapp.com')
            .then( console.log("node is up") )
            .catch( (err) => console.error(err) );
    }

    addCurrentUserToPeople(nextState){

        const isJoinedAlready = false; //Object.keys(nextState.people).map(c => nextState.people[c].user.uid).includes(nextState.user.uid);

        if(!isJoinedAlready) {
          const user = {
            data: {
                user: nextState.user
            }
          }
          console.log("adding user to people",nextState.user,user)
          base.push('/people', user ).onDisconnect().remove();
        }
    }

    removeCurrentUserFromPeople(people, user) {
        console.log("removePeople",people)
        Object.keys(people)
        .map((key, index) => {
            if (people[key].user.uid === user.uid) {
                base.database().ref(`/people/${people[key].key}`).remove()  
                return false;
            }
            return people[key].user.uid;
        })
    }

    onLogout() {
        // remove the current person from the chatroom when you logout
        this.setState( {loggedIn: false});
        this.removeCurrentUserFromPeople(this.state.people, this.state.user);
        clearTimeout(this.checkingVerifiedTimeout);

        base.auth().signOut();
    }

    checkUserVerified(){
        console.log("checkuserverified")
        base.auth().onAuthStateChanged(firebaseUser => {
            if (firebaseUser) {
                if (firebaseUser.emailVerified===true){
                    this.setState({emailVerified:true})
                } else {
                    this.checkingVerifiedTimeout = setTimeout( this.checkUserVerified, 2000);
                }
            } else {
                clearTimeout(this.checkingVerifiedTimeout);  
            }
        });

    }

    componentWillMount() {
        let endpoint = '';
        // get chatlist from firebase
        this.ref3 = base.bindToState(`/people`, {
            context: this,
            state: 'people',
            asArray: true
        });

        base.auth().onAuthStateChanged(firebaseUser => {

            // sync user data when s/he logs in, reset modal
            this.setState({
                loggedIn: (null !== firebaseUser),
                modalIsOpen:false
            });

            if (firebaseUser) {
                const { emailVerified, email } = firebaseUser;
                console.log(firebaseUser)
                this.setState({modal2IsOpen:!emailVerified, emailVerified, email})

                endpoint = `/users/${firebaseUser.uid}/public`;
                this.setState({
                    uid: firebaseUser.uid
                })
                console.log("Logged IN", endpoint);
                this.ref1 = base.bindToState(endpoint, {
                    context: this,
                    state: 'user'
                });
                this.ref4 = base.bindToState(`/users/${firebaseUser.uid}/invites`, {
                    context: this,
                    state: 'invites'
                });
                this.checkingVerifiedTimeout = setTimeout( this.checkUserVerified , 2000);    


            } else {
                if (this.ref1) {base.removeBinding(this.ref1)};
                if (this.ref4) {base.removeBinding(this.ref4)};
                console.log('Not logged in');
                const user = {};
                this.setState({
                    user,
                    uid: ''
                });
            }
        });
    }

    componentWillUnmount() {
        if (this.ref1) {base.removeBinding(this.ref1)};
        if (this.ref3) {base.removeBinding(this.ref3)};
    }

    saySend(say) {
        // prepare the new message, and then send it firebase

        const message = {
            text: say,
            time: Date.now(),
            user: this.state.user
        };

        console.log(message, this.state)

        base.push("/messages", {
            data: message
        })
    }

    componentWillUpdate(nextProps, nextState) { 
        // when you've registered or logged in, you have to add yourself to the chatroom list  -- TRICKY!!

        // when you come back from editing your profile, you have to update your user info
        const isNextStateUser = undefined !== nextState.user.uid
        const isStateUser = undefined !== this.state.user.uid;
        //const isNextStatePeople = nextState.people.length>0;
        const isStatePeople = this.state.people.length>0;

        if (isNextStateUser && !isStateUser ) {
            const firstLogin = nextState.user && !nextState.user.learnedMore;
            if (firstLogin)  {
                base.update(`/users/${nextState.user.uid}/public`, {data: {learnedMore: true}});
                this.setState({modal2IsOpen: true});
            }
        }

        if ((isNextStateUser && !isStateUser && isStatePeople) ||
            (isStateUser && !isStatePeople && isStatePeople)) {
            // getting user & have people already, or getting people and have user already
                this.addCurrentUserToPeople(nextState);
            }

        if (!isNextStateUser && isStateUser) {
            // user just logged out so remove from people list
            console.log("logging out");
        }
        if (nextState.user.dirty && isStatePeople && isStateUser ) {
            console.log("dirty", nextState)
            this.removeCurrentUserFromPeople(nextState.people, nextState.user);
            this.addCurrentUserToPeople(nextState);
            base.update(`/users/${this.state.user.uid}/public`, {data: {dirty: false}})
        }
    }


  render() {

    const customStyles = {
          content : {
            top                   : '50%',
            left                  : '50%',
            right                 : '15%',
            bottom                : 'auto',
            marginRight           : '-50%',
            transform             : 'translate(-50%, -50%)',
            height                : '85%', 
            overlfow              : 'scroll',
            textAlign             : 'center',
            zIndex                : '999',
            position              : 'absolute'
        },
          overlay : {
            backgroundColor   : 'rgba(56,49,68,0.5)'
        }
    };
    const loginRegister = (
        <div>
        <a href="#"  style={{alignText:'left'}} onClick={()=>this.setState({modalIsOpen:false})}>x close</a>

        <Grid>                 
            <Col xs={12} sm={5} md={5} lg={5} className="text-center"><Register /></Col>
                <Col xs={12} sm={5} md={5} lg={5} className="text-center"><Login /></Col>
        </Grid>
        </div>)

    const joinButton = !this.state.loggedIn ? (<Button onClick={ () => {
                    this.setState({modal2IsOpen:false})
                    this.setState({modalIsOpen: true})
                }} bsStyle="primary" bsSize="large">Join now</Button>) 
    : '';

    const privacyPolicy = (
        <Modal
            isOpen={ this.state.modal3IsOpen }
            onRequestClose={ ()=>this.setState({modal3IsOpen: false}) }
            style={customStyles}
            contentLabel="Privacy policy">
            <a href="#" onClick={()=>{this.setState({modal3IsOpen:false}); console.log("close")}}>x close</a>

            <Privacy />

        </Modal>                  
    )

    const closeOptions = this.state.emailVerified ? 
        <a href="#" onClick={()=>{this.setState({modal2IsOpen:false}); console.log("close")}}>x close</a>
        :   <Alert bsStyle="info"><h1>Please verify your email</h1> <p>Please click on the link we have sent to {this.state.email}.</p><p> Having trouble? <a href="#" onClick={()=>{
                base.auth().currentUser.sendEmailVerification();
                alert(`Email sent. Please ${this.state.email} for your link.`);   
            }}>Resend email</a> or <a href="#" onClick={()=>{
                this.setState({modal2IsOpen:false, modalIsOpen:true})
                this.onLogout();
            }}>start over</a> </p></Alert>

    const learnMore = (
        <Modal
            isOpen={ this.state.modal2IsOpen }
            onRequestClose={ ()=> {if (this.state.emailVerified) { this.setState({modal2IsOpen: false})}} }
            style={customStyles}
            contentLabel="Learn more"
        > 

            <div className="row">
                            {closeOptions}

                <h2>Find someone to practice with, easily!</h2>
            </div>
            <div className="row">
                <div className='avatar easy col-xs-1 col-xs-offset-2 col-sm-1 col-sm-offset-3 col-md-1 col-md-offset-4'>1</div> 
                <div className='col-xs-7 col-sm-5 col-md-4'><h3>Chat with students</h3></div>
            </div>
            <br/>
            <div className="row"> 
                <div className='avatar easy col-xs-1 col-xs-offset-2 col-sm-1 col-sm-offset-3 col-md-1 col-md-offset-4'>2</div> 
                <div className='col-xs-7 col-sm-5 col-md-4'><h3>Pick your partner</h3></div>
            </div>
            <br/>
            <div className="row">
                <div className='avatar easy col-xs-1 col-xs-offset-2 col-sm-1 col-sm-offset-3 col-md-1 col-md-offset-4'>3</div>
                <div className='col-xs-7 col-sm-5 col-md-4'><h3>Practice by video!</h3></div>
            </div>             
            <br/>
            <div className="row">
               {joinButton}
                &nbsp;&nbsp;&nbsp;
            </div>
              <div className="row">
                <div className='col-xs-8 col-xs-offset-2'>
                <p><i>"Practice only on days you eat!"</i></p>
                </div>
            </div>
        </Modal>);

        var body;
        if (this.state.loggedIn) {

            if (this.state.user.username) {

                body =
                    <div className="row">
			 	 
             		<div className="col-sm-8">
				  		<WaitingRoom saySend={this.saySend} 
                        user={this.state.user} 
                        invites={this.state.invites} />
				 	</div>
				 	<div className="col-sm-4">
				 		<Waiting people={this.state.people} 
                            user={this.state.user} 
                            invites={this.state.invites}/> 
				 	</div> 
                    { privacyPolicy }                            

				</div>
            } else {
                body = <div>Fill out user profile</div>
            }
        } else {
            body =
                <div>
                    <section className="content-section video-section">
                      <div className="pattern-overlay">
                        <div id="bgndVideo" className="player">
                            <video loop muted autoPlay poster="/media/homepage-poster.jpg" alt="Live earning lessons" src="/media/homepage-video.mp4" type="video/mp4" />
                        </div>
                        <div className="overlay-text">

                       <div className="container">

                      <div className="row">
                        <div className="col-sm-6 col-sm-offset-3">
                            <div className="text-center">
                                <h1>Hello, Musicians!</h1>
                                <h3>Let's make Suzuki delightful -- not hard!</h3>
                                <br/>
                            </div>
                        </div>
                      </div>

                      <div className="row">

                        <Button href="#" onClick={()=>this.setState({modalIsOpen: true})}>Login</Button>
                        &nbsp;&nbsp;&nbsp;

                         <Button onClick={()=>this.setState({modalIsOpen: true})} bsStyle="primary" bsSize="large">Join now</Button>
                         <Modal
                         isOpen={ this.state.modalIsOpen }
                         onRequestClose={ ()=> this.setState({modalIsOpen: false}) }
                         style={customStyles}
                         contentLabel="Perfect Practice"
                         >      
                        { loginRegister }
                        If you are 12 years old or younger, you must register with your parent or guardian's email address. Please review our <a href="#" onClick={()=>
                                this.setState({modal3IsOpen: true})}>privacy policy</a>. 
                         </Modal>

                        &nbsp;&nbsp;&nbsp;
                        <a href="#" onClick={()=>this.setState({modal2IsOpen: true})} className='learn-more'>Learn more</a>
                        { privacyPolicy }                            
                     </div>
                </div>
                        </div>
                      </div>
                    </section>   
                </div>
        }

    const navcolor = this.state.loggedIn ? 'perfect-blue logged-in' : 'perfect-white logged-out'

    const branding = <Link to="/" className={navcolor}><img height="28" style={{verticalAlign: 'sub'}} src="/media/violin.svg" /><span className="logo-text">PerfectPractice.co</span></Link> 

    const secondaryNav = <div className="logout"><a href="#" onClick={()=>this.setState({modal3IsOpen:true})}>Privacy</a> &bull; <a href="#" onClick={this.onLogout}>Logout</a></div>

    const nav =  (<div className="row">
                    {branding}{this.state.loggedIn ? secondaryNav : ''} 
                  </div>) 

        return (this.state.loggedIn) ?
            (<div style={signincss} className="container">
    				{nav}
    				{body}
                                             { learnMore }

    		</div>) :
           (<div className="container">
                    {nav}
                    {body}
                                             { learnMore }

            </div>)             
    }
}

export default App;
