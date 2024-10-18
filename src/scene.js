import * as THREE from "three";
import {OrbitControls} from 'https://unpkg.com/three/examples/jsm/controls/OrbitControls.js';

import { createCamera } from './camera.js';
import { createOrigin } from './objects/origin.js';
import { createBlob, createDrone } from './objects/blob.js';
import { createWorldCam, worldCamSetPose } from "./objects/world_cam.js";
import { drawArrow } from "./objects/arrow.js";

// Fetch stuff
function fetchCamPoses(){
    fetch('http://127.0.0.1:5000/camera_poses')
    .then((response) => response.json())
    .then((data) => {
        CAM_POSE_DATA = data["camera_poses"];

        console.log('POSE_DATA:', CAM_POSE_DATA);
        


        return data;
    })
    .catch((error) => {
        console.error("Error fetching POSE_DATA:", error);
        
    });
}

function fetchPointPosition(){
    if (TRIANGULATE_FLAG) {
        fetch('http://127.0.0.1:5000/get_point_location')
        .then((response) => response.json())
        .then((data) => {
            POINT_COORDS = [data["x"], data["y"], data["z"]];
            
            // Convert to meters
            POINT_COORDS = POINT_COORDS.map((coord) => coord/1000);
            
            // console.log('Point location:', POINT_COORDS);
        });
    }
}
function fetchObjectPosition(){
    if (TRIANGULATE_FLAG) {
        fetch('http://127.0.0.1:5000/get_drone_location')
        .then((response) => response.json())
        .then((data) => {
            let pos = data["pos"]
            let heading_rad = data["heading"]
            POINT_COORDS = [pos["x"], pos["y"], pos["z"]];
            
            // Convert to meters
            POINT_COORDS = POINT_COORDS.map((coord) => coord/1000);
            DRONE_HEADING_RAD = heading_rad;
            // console.log('Point location:', POINT_COORDS);
        });
    }
}

// Flags for backend
function flagStartTriangulation(){
    fetch('http://127.0.0.1:5000/start_triangulation')
    .then((response) => response.json())
    .then((data) => {
        
        console.log('flagStartTriangulation : ', data);
    })
}
function flagStopTriangulation(){
    fetch('http://127.0.0.1:5000/stop_triangulation')
    .then((response) => response.json())
    .then((data) => {
        console.log('flagStopTriangulation : ', data);
    })
}

function fireUpCameras(){
    fetch('http://127.0.0.1:5000/fire_up_cameras')
    .then((response) => response.json())
    .then((data) => {
        console.log('FireUpCameras : ', data);
    });
}

// 3js functions
function removeExpendibleShit(){
    console.log('Removing '+ expendible_shit.length + ' things...');
    while(expendible_shit.length > 0){ 
        // expendible_shit.remove(expendible_shit[0]);
        scene.remove(expendible_shit.pop());
    }
}
function startTriangulation() {
    
    flagStartTriangulation();
    console.log('Starting Triangulation...');
    TRIANGULATE_FLAG = true;

}
function stopTriangulation() {
    flagStopTriangulation();
    TRIANGULATE_FLAG = false;
    console.log('Stopping Triangulation...', TRIANGULATE_FLAG);
}



let TRIANGULATE_FLAG = false;

let CAM_POSE_DATA = {};
let POINT_COORDS = [];
let DRONE_HEADING_RAD = 0;
let orbitControls;

let expendible_shit = [];
let FUCKTHEARROW = null;

let PEN_UP = false;


const scene = new THREE.Scene();

export function createScene() {
    // Initial scene setup
    const gameWindow = document.getElementById('render-target');
    // const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x777777);
    

    const camera = createCamera(gameWindow);


    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(gameWindow.offsetWidth, gameWindow.offsetHeight);
    gameWindow.appendChild(renderer.domElement);


    
    fetchCamPoses();

    /* CONVENTIONS
    
    3JS COORDINATES
    - X Towards you | Z Left | Y Up 
    
    - rotation.x // Roll
    - rotation.y // Yaw
    - rotation.z // Pitch
    
    GAZEBO COORDINATES
    - X Towards you | Y Left | Z Up
    
    
    - 1 is 1 meter
    - 0.1 is 10 cm
    - 0.01 is 1 cm
    - 0.001 is 1 mm



    NUM_OF_CAMS = 3

    */

    // Create Objects ------------------------------------------------------------
    createOrigin(scene, 0.01);

    
    // let draw_blob = true;
    
    let blob = createBlob(scene, [0,0,0], 0.05, "m", 0xc41dde, true);
    // let blob = createDrone(scene, [0,0,0], 0.05, "m", 0xc41dde, true);
    
    // let worldCam1 = createWorldCam(scene, 0.01);
    // let worldCam2 = createWorldCam(scene, 0.01);
    // let worldCam3 = createWorldCam(scene, 0.01);


    orbitControls = new OrbitControls(camera.camera, renderer.domElement);
    
    // ANIMATION LOOP------------------------------------------------------------
    function draw() {

        // fetchPointPosition();
        fetchObjectPosition();


        // // Camera State
        // if (Object.keys(CAM_POSE_DATA).length > 0) {
        //     // Assuming only 3 cams
            
        //     worldCamSetPose(worldCam1, CAM_POSE_DATA[0]["R"], CAM_POSE_DATA[0]["t"]);
            
        //     // console.log(CAM_);
        //     if (CAM_POSE_DATA[1]["R"] != [null, null, null]) {
        //         worldCamSetPose(worldCam2, CAM_POSE_DATA[1]["R"], CAM_POSE_DATA[1]["t"]);
        //     }
        //     // if (CAM_POSE_DATA[2]["R"] != [null, null, null]) {
        //         //     worldCamSetPose(worldCam3, CAM_POSE_DATA[2]["R"], CAM_POSE_DATA[2]["t"]);
        //         // }
        // }
        
        
        // XYZ
        if (Object.keys(POINT_COORDS).length > 0) {
            blob.position.x = POINT_COORDS[0];
            blob.position.y = POINT_COORDS[1];
            blob.position.z = POINT_COORDS[2];
            if (!PEN_UP) {
                expendible_shit.push(createBlob(scene, [POINT_COORDS[0], POINT_COORDS[2], POINT_COORDS[1]], 0.015, "m", 0x33ffc4, false));
            }
        
            scene.remove(FUCKTHEARROW);
            // DRONE_HEADING_RAD
            FUCKTHEARROW = drawArrow(scene, [POINT_COORDS[0], POINT_COORDS[2], POINT_COORDS[1]], [DRONE_HEADING_RAD,0 , 0], 0.2, 0xFFFF00);
        }
        


        // blob.position.set(1,1,1);

        orbitControls.update();
        renderer.render(scene, camera.camera);
    }



    function start() {
        renderer.setAnimationLoop(draw);
    }
    function stop() {
        renderer.setAnimationLoop(null);
    }
  
    function setIsometricView() {
        camera.setIsometricView(orbitControls);
    }
    function lookAtOrigin() {
        camera.lookAtOrigin(orbitControls);
    }

    function togglePen(){
        if(PEN_UP){
            PEN_UP = false;
        }else{
            PEN_UP = true;
        }
    }




    return {
        camera,
        start, stop,
        setIsometricView, lookAtOrigin, removeExpendibleShit,

        fireUpCameras, startTriangulation, stopTriangulation, togglePen

    }

}