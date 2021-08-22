//
//  ViewController.swift
//  Mano
//
//  Created by Goncalo Palaio on 21/08/2021.
//

import Cocoa
import PythonKit

class ViewController: NSViewController {
    var generalScripts: PythonObject!
    
    @IBOutlet var mainNSTextView: NSTextView!

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        
        view.window?.makeFirstResponder(self)
        mainNSTextView.delegate = self
        
        let sys = Python.import("sys")
        sys.path.append("/Users/goncalopalaio/Documents/projects/Mano/scripts/")
        
        print("Python \(sys.version_info.major).\(sys.version_info.minor)")
        print("Python Version: \(sys.version)")
        print("Python Encoding: \(sys.getdefaultencoding().upper())")
        
        generalScripts = Python.import("mano_general")
        
        refreshContent()
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }
    
    func refreshContent() {
        DispatchQueue.global(qos: .userInitiated).async {
            print("starting")
            let result = self.generalScripts.get_html_content()
        
            let data = Data("\(result)".utf8)
            
            if let attributedString = try? NSAttributedString(data: data, options: [.documentType: NSAttributedString.DocumentType.html], documentAttributes: nil) {
                print("calling main")
                
                DispatchQueue.main.async {
                    print("entering main")
                    self.mainNSTextView.string = ""
                    self.mainNSTextView.performValidatedReplacement(in: NSRange(), with: attributedString)
                    print("exiting main")
                }
            }
            //self.showError()
        }
    }
    
    func showError() {
        DispatchQueue.main.async {
            print("Some kind of error happened")
        }
    }

}

extension ViewController: NSTextViewDelegate {
    func textView(_ textView: NSTextView, clickedOnLink link: Any, at charIndex: Int) -> Bool {
        print("textView: | \(link) | \(charIndex)")
        
        if let linkString = link as? NSString {
            print("Clicked on string link: \(linkString)")
            return handleLink(linkString as String)

        } else if let linkNSUrl = link as? NSURL {
            print("Clicked on NSUrl link: \(linkNSUrl)")

            guard let linkString = linkNSUrl.absoluteString else {
                return false
            }
            
            return handleLink(linkString)
        }
        return false
    }
    
    private func handleLink(_ link: String) -> Bool {
        if (!link.starts(with: "mano://")) {
            return false
        }
        let actionId = link.replacingOccurrences(of: "mano://", with: "")
        
        print("handleLink: Handling actionId: \(actionId)")
        
        DispatchQueue.global(qos: .userInitiated).async {
            let value = self.generalScripts.do_action(actionId)
            
            self.refreshContent()
            print("handleLink: result: \(value.was_successful) msg: \(value.message)")
        }
        
        return true
    }
}
