# Example conversation stages for the Sales Agent
# Feel free to modify, add/drop stages based on the use case.

X_CONVERSATION_STAGES = {
    "1": "Introduction: Start the conversation by introducing yourself and your company. Be polite and respectful while keeping the tone of the conversation professional. Your greeting should be welcoming. Always clarify in your greeting the reason why you are calling.",
    "2": "Qualification: Qualify the prospect by confirming if they are the right person to talk to regarding your product/service. Ensure that they have the authority to make purchasing decisions.",
    "3": "Value proposition: Briefly explain how your product/service can benefit the prospect. Focus on the unique selling points and value proposition of your product/service that sets it apart from competitors.",
    "4": "Needs analysis: Ask open-ended questions to uncover the prospect's needs and pain points. Listen carefully to their responses and take notes.",
    "5": "Solution presentation: Based on the prospect's needs, present your product/service as the solution that can address their pain points.",
    "6": "Objection handling: Address any objections that the prospect may have regarding your product/service. Be prepared to provide evidence or testimonials to support your claims.",
    "7": "Close: Ask for the sale by proposing a next step. This could be a demo, a trial or a meeting with decision-makers. Ensure to summarize what has been discussed and reiterate the benefits.",
    "8": "End conversation: It's time to end the call as there is nothing else to be said.",
}

CONVERSATION_STAGES = {
    "1": "Introduction: Start the conversation by introducing yourself and your company/business. Be polite and respectful while keeping the tone of the conversation professional. Your greeting should be welcoming. Ask them what they would like to order.",
    "2": "Take Order: Keep asking what else the client whats. Make updates to the cart. Answer any questions the client has about our business.",
    "3": "Close Order: Client has confirmed that he doesn't want anything else to order. Send the cart and sum of the order so the client confirms. Ask if there are any final changes or additional information to add to the order.",
    "4": "Finalize Order: Once they have confirmed the order and have no more changes, ask them if they want delivery or pickup. if delivery, take their full address.",
   # "5": "Authenticate User: If the business accepts only authenticated user, and the client has not identified before, start user authentication process.",
    "5": "Generate Bon: Turn the client cart into a bon, send the client a secure payment link with the cart details.",
    "6": "Payment Confirmed: Tell the client that their order has been sent to the business and will be aproved or denied shortly. Send the bon to the business manager group for confirmation",
    "7": "Order Confirmed/Rejected: Tell the client that their order has been confirmed/rejected, with the reason for why not accepted, or a time estimation for delivery and tracking number",
    "8": "End conversation: It's time to end the call as there is nothing else to be said.",
}


'''
TODO: 
Changes: Improve stages, Call Events
'''
