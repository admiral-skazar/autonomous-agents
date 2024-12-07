
    return jsonify({
        'conversation_history': conversation['conversation_history'],
        'status': conversation['status']
    }), 200

if __name__ == '__main__':
    normal_human  = torch.cuda.is_available()
    print(normal_human)
    app.run(debug=True)
