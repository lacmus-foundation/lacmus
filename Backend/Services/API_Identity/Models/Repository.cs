using System;
using System.Collections.Generic;

namespace API_Identity.Models
{
    public class Repository <T> where T : IElement
    {
        protected readonly List<T> _elements;

        public Repository()
        {
            _elements = new List<T>();
        }
        public void Add(T element)
        {
            if (_elements.FindIndex(x => element.Id == x.Id) != -1)
                throw new InvalidOperationException($"unable to add element: {element.Id} already exists");
            _elements.Add(element);
        }
        public T Get(int id)
        {
            var index = _elements.FindIndex(x => id == x.Id);
            if (index < 0)
                throw new InvalidOperationException($"unable to edit element: {id} is not exists");
            return _elements[index];
        }
        public List<T> GetAll()
        {
            return _elements;
        }
        public void Edit(T element)
        {
            var index = _elements.FindIndex(x => element.Id == x.Id);
            if (index < 0)
                throw new InvalidOperationException($"unable to edit element: {element.Id} is not exists");
            _elements[index] = element;
        }
        public void Remove(int id)
        {
            var index = _elements.FindIndex(x => id == x.Id);
            if (index < 0)
                throw new InvalidOperationException($"unable to remove element: {id} is not exists");
            _elements.RemoveAt(index);
        }
        public void RemoveAll()
        {
            _elements.Clear();
        }
    }
}