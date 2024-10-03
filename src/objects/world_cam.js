import * as THREE from "three";
import { gazeboCoords2THREE } from '../utils.js'

export function createWorldCam(scene, scaler=1, position = [0, 0, 0], rotation = [0,0,0], unit = 'm', transparent=false, color = 0xc41dde) {
    
    let radius = 50 * scaler;
    let height = 50 * scaler;

    if (unit == "mm") {
        position = position.map(x => x / 1000);
        radius = radius / 1000;
        height = height / 1000;
    }



    position = gazeboCoords2THREE(position);
    rotation = gazeboCoords2THREE(rotation);



    var geometry = new THREE.ConeGeometry(radius, height, 4);
    let material = new THREE.MeshBasicMaterial({ color: color });
    

    const PYRAMID = new THREE.Mesh(geometry, material);

    scene.add(PYRAMID);

    // Wireframe
    const wireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry),
        new THREE.LineBasicMaterial({ color: 0x000000 }) // Black border color
    );
    PYRAMID.add(wireframe);

    PYRAMID.position.x = position[0];
    PYRAMID.position.y = position[1];
    PYRAMID.position.z = position[2];

    // PYRAMID.rotation.x = rotation[0] + Math.PI / 4; // 45 degrees
    // PYRAMID.rotation.y = rotation[1]; // 90 degrees
    // PYRAMID.rotation.z = rotation[2] + Math.PI / 2; // 90 degrees

    PYRAMID.rotation.x = rotation[0] + Math.PI / 2; // 45 degrees
    PYRAMID.rotation.y = rotation[1] + Math.PI / 4; // 90 degrees
    PYRAMID.rotation.z = rotation[2]; // 90 degrees

    return PYRAMID;
}

export function worldCamSetPose(wc, position, rotation, unit = 'm') {


    if (unit == "mm") {
        position = position.map(x => x / 1000);
    }
    
    wc.position.x = position[0];
    wc.position.y = position[1];
    wc.position.z = position[2];

    wc.rotation.x = rotation[0] + Math.PI / 2;
    wc.rotation.y = rotation[1] + Math.PI / 4;
    wc.rotation.z = rotation;

    return wc;
}