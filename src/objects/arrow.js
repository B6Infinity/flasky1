import * as THREE from "three";
import {gazeboCoords2THREE} from '../utils.js'

export function drawArrow(scene, origin = [0,0,0], dir = [0.1,0.1,0.1], length=1, color = 0xc41dde) {

    origin = gazeboCoords2THREE(origin);
    dir = gazeboCoords2THREE(dir);

    const DIR = new THREE.Vector3( dir[0], dir[1], dir[2] );

    //normalize the direction vector (convert to vector of length 1)
    DIR.normalize();

    const ORIGIN = new THREE.Vector3(origin[0], origin[1], origin[2]);

    const arrowHelper = new THREE.ArrowHelper( DIR, ORIGIN, length, color );
    scene.add(arrowHelper);
    
    return arrowHelper;
}