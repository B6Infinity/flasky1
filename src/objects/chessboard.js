import * as THREE from "three";
import { gazeboCoords2THREE } from '../utils.js'

export function createChessboard(scene, position = [0, 0, 0], chessboard_square_mm = 12, squares_in_row = 7, transparent=false, color = 0xc41dde) {

    position = gazeboCoords2THREE(position);

    const chessboard_edge = chessboard_square_mm * squares_in_row / 100;

    let geometry = new THREE.BoxGeometry(chessboard_edge, chessboard_edge, 0.05);
    let material = new THREE.MeshBasicMaterial({ color: color });
    

    const CHESSBOARD = new THREE.Mesh(geometry, material);

    scene.add(CHESSBOARD);

    // Wireframe
    const wireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry),
        new THREE.LineBasicMaterial({ color: 0x000000 }) // Black border color
    );
    CHESSBOARD.add(wireframe);

    CHESSBOARD.position.x = position[0];
    CHESSBOARD.position.y = position[1];
    CHESSBOARD.position.z = position[2];


    return CHESSBOARD;
}