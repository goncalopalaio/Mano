//
//  MyNSWindowController.swift
//  Mano
//
//  Created by Goncalo Palaio on 22/08/2021.
//

import Foundation
import Cocoa

class MyNSWindowController: NSWindowController {
    @IBAction func refreshToolbarClick(_ sender: NSToolbarItem) {
        let viewController = contentViewController as! ViewController
        viewController.refreshContent()
    }
}
    
