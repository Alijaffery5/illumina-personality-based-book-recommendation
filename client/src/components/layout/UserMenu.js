import React, { Component } from 'react'

import { Link } from 'react-router-dom'
import {logout, getUser} from '../Services'

export class UserMenu extends Component {

    constructor(){
        super()
        this.state ={
            user: {}
        }
    }

    logOut (e) {
        e.preventDefault()
        localStorage.removeItem('logged_in')
        
        logout().then(res =>{
            window.location.href = "http://localhost:3001"
        })
    }

    componentDidMount(){        
        getUser().then(res => {
            this.setState({user: JSON.parse(res.data.user)})
        }).catch(err =>{
            alert(err)
        })

    }

    render() {

        const { profile_pic } = this.state.user
        
        return (
            <li className="nav-item dropdown ml-auto">
                <Link to="#" className="nav-link dropdown-toggle" id="navDropDownLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <img alt="" src={profile_pic} 
                width="32" height="32" className="rounded-circle img-fluid" style={{border: '2px solid black'}} />
                &nbsp;Profile
                </Link>
                <div className="dropdown-menu" aria-labelledby="navDropDownLink">
                    <Link className="dropdown-item" to="#">Preferences</Link>
                    <div className="dropdown-divider"></div>
                    <Link className="dropdown-item" to="#" onClick={this.logOut.bind(this)}>Logout</Link>
                </div>
            </li>
        )
    }
}

export default UserMenu