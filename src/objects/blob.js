import * as THREE from "three";
import {gazeboCoords2THREE} from '../utils.js'

export function createBlob(scene, position = [0,0,0], size=1, unit = 'm', color = 0xc41dde, wireframe = true) {

    if (unit == "mm") {
        position = position.map(x => x / 1000);
        size = size / 1000;
    }

    position = gazeboCoords2THREE(position);

    let geometry = new THREE.BoxGeometry(size,size,size);
    let material = new THREE.MeshBasicMaterial({color: color});

    
    const BLOB = new THREE.Mesh(geometry, material);

    scene.add(BLOB);

    // Wireframe
    if (wireframe){
        const wireframe = new THREE.LineSegments(
            new THREE.EdgesGeometry(geometry),
            new THREE.LineBasicMaterial({ color: 0x000000 }) // Black border color
        );
        BLOB.add(wireframe);
    }


    BLOB.position.x = position[0];
    BLOB.position.y = position[1];
    BLOB.position.z = position[2];

    return BLOB;
}