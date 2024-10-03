import * as THREE from "three";

export function createCamera(gameWindow, camRadius=1.7, camAzimuth=0, camElevation=0) {
    const DEG2RAD = Math.PI / 180;

    const camera = new THREE.PerspectiveCamera(75, gameWindow.offsetWidth / gameWindow.offsetHeight, 0.1, 1000);

    camera.position.set( 1, 1, 1 );
    updateCameraPosition();

    function setIsometricView(orbitControls) {
        camera.position.set( 1, 1, 1 );
        // camera.position.set(2, 2, 2);
        
        camera.lookAt(0,0,0);

        orbitControls.target.set(0,0,0);
        // orbitControls.update();

        updateCameraPosition();
        console.log('Set Isometric View');
    }
    
    function lookAtOrigin(orbitControls) {
        camera.lookAt(0,0,0);
        orbitControls.target.set(0,0,0);
        // orbitControls.update();


        updateCameraPosition();
    }
    
    
    function updateCameraPosition() {
        camera.updateMatrix();        
    }
    
 

    return {
        camera,
        setIsometricView, lookAtOrigin
    };
}